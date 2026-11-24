from abc import ABC, abstractmethod
import os
import subprocess
import wave
import json
from typing import Dict, Any, List

class TTSProvider(ABC):
    @abstractmethod
    def generate(self, text: str, output_path: str) -> Dict[str, Any]:
        """Generate speech audio from text and return timing metadata."""
        raise NotImplementedError

class WindowsSAPIProvider(TTSProvider):
    """Local offline TTS provider using direct Windows SAPI COM dispatch with PowerShell fallback."""
    
    def __init__(self, voice_name: str = None):
        self.voice_name = voice_name
    
    def generate(self, text: str, output_path: str) -> Dict[str, Any]:
        abs_output = os.path.abspath(output_path).replace("\\", "/")
        os.makedirs(os.path.dirname(abs_output), exist_ok=True)
        
        # 1. Preferred Direct Native COM execution (fast, secure, zero subprocess injection risk)
        com_success = False
        try:
            import win32com.client
            voice = win32com.client.Dispatch("SAPI.SpVoice")
            stream = win32com.client.Dispatch("SAPI.SpFileStream")
            if self.voice_name:
                for v in voice.GetVoices():
                    if self.voice_name.lower() in v.GetDescription().lower():
                        voice.Voice = v
                        break
            stream.Open(abs_output, 3, False)
            voice.AudioOutputStream = stream
            voice.Speak(text)
            stream.Close()
            com_success = True
        except Exception:
            com_success = False

        # 2. Fallback to PowerShell if COM dispatch is unavailable
        if not com_success:
            self._powershell_fallback(text, abs_output)
            
        with wave.open(abs_output, "rb") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            duration_sec = frames / float(rate)
            
        return {
            "output_path": abs_output,
            "duration_seconds": round(duration_sec, 3),
            "sample_rate": rate,
            "frames": frames
        }

    def _powershell_fallback(self, text: str, abs_output: str):
        safe_text = text.replace("`", "``").replace('"', '`"').replace("$", "`$")
        voice_select_script = ""
        if self.voice_name:
            voice_select_script = f"""
$selected = $voice.GetVoices() | Where-Object {{ $_.GetDescription() -like "*{self.voice_name}*" }} | Select-Object -First 1
if ($selected) {{ $voice.Voice = $selected }}
"""
        ps_script = f"""
$stream = New-Object -ComObject SAPI.SpFileStream
$stream.Open("{abs_output}", 3, $false)
$voice = New-Object -ComObject SAPI.SpVoice
{voice_select_script}
$voice.AudioOutputStream = $stream
$voice.Speak("{safe_text}")
$stream.Close()
"""
        temp_ps = os.path.join(os.path.dirname(abs_output), f"_synth_{os.path.basename(abs_output)}.ps1")
        with open(temp_ps, "w", encoding="utf-8") as f:
            f.write(ps_script)
        try:
            cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", temp_ps]
            subprocess.run(cmd, capture_output=True, text=True, check=True)
        finally:
            if os.path.exists(temp_ps):
                try:
                    os.remove(temp_ps)
                except Exception:
                    pass

def format_srt_time(seconds: float) -> str:
    millis = int(round((seconds - int(seconds)) * 1000))
    total_seconds = int(seconds)
    secs = total_seconds % 60
    mins = (total_seconds // 60) % 60
    hours = total_seconds // 3600
    return f"{hours:02d}:{mins:02d}:{secs:02d},{millis:03d}"

class NarrationManager:
    def __init__(self, provider: TTSProvider = None):
        self.provider = provider or WindowsSAPIProvider(voice_name="David")
        
    def process_script(self, script_path: str, output_dir: str) -> Dict[str, Any]:
        with open(script_path, "r", encoding="utf-8") as f:
            script_data = json.load(f)
            
        os.makedirs(output_dir, exist_ok=True)
        audio_dir = os.path.join(output_dir, "audio_segments")
        os.makedirs(audio_dir, exist_ok=True)
        
        timeline = []
        current_time = 0.0
        fps = 30
        
        srt_entries = []
        combined_wav_path = os.path.join(output_dir, "06_narration.wav")
        segment_files = []
        
        for idx, seg in enumerate(script_data["segments"], start=1):
            seg_id = seg["segment_id"]
            text = seg["text"]
            seg_wav = os.path.join(audio_dir, f"{seg_id}.wav")
            
            meta = self.provider.generate(text, seg_wav)
            duration = meta["duration_seconds"]
            segment_files.append(seg_wav)
            
            # Pad each segment with 0.5s pause so speech has breathing room
            padded_duration = duration + 0.5
            start_time = current_time
            end_time = current_time + padded_duration
            
            timeline_entry = {
                "segment_id": seg_id,
                "text": text,
                "audio_file": seg_wav.replace("\\", "/"),
                "raw_duration_seconds": duration,
                "duration_seconds": round(padded_duration, 3),
                "start_seconds": round(start_time, 3),
                "end_seconds": round(end_time, 3),
                "start_frame": int(round(start_time * fps)),
                "end_frame": int(round(end_time * fps)),
                "duration_frames": int(round(padded_duration * fps))
            }
            timeline.append(timeline_entry)
            
            srt_start = format_srt_time(start_time)
            srt_end = format_srt_time(start_time + duration)
            srt_entries.append(f"{idx}\n{srt_start} --> {srt_end}\n{text}\n")
            
            current_time = end_time

        self._combine_wavs(segment_files, timeline, combined_wav_path)
        
        timeline_path = os.path.join(output_dir, "07_narration_timeline.json")
        with open(timeline_path, "w", encoding="utf-8") as f:
            json.dump({
                "schema_version": "1.0",
                "total_duration_seconds": round(current_time, 3),
                "total_frames": int(round(current_time * fps)),
                "fps": fps,
                "segments": timeline
            }, f, indent=2)
            
        srt_path = os.path.join(output_dir, "08_subtitles.srt")
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(srt_entries))
            
        return {
            "combined_audio": combined_wav_path.replace("\\", "/"),
            "timeline": timeline_path.replace("\\", "/"),
            "subtitles": srt_path.replace("\\", "/"),
            "total_duration_seconds": round(current_time, 3),
            "total_frames": int(round(current_time * fps)),
            "segments": timeline
        }
        
    def _combine_wavs(self, file_list: List[str], timeline: List[Dict[str, Any]], output_wav: str):
        if not file_list:
            return
            
        with wave.open(file_list[0], 'rb') as first_wf:
            params = first_wf.getparams()
            
        with wave.open(output_wav, 'wb') as out_wf:
            out_wf.setparams(params)
            sample_rate = params.framerate
            n_channels = params.nchannels
            sampwidth = params.sampwidth
            
            silence_frame = b'\x00' * (n_channels * sampwidth)
            
            for file_path, entry in zip(file_list, timeline):
                with wave.open(file_path, 'rb') as in_wf:
                    data = in_wf.readframes(in_wf.getnframes())
                    out_wf.writeframes(data)
                
                pad_sec = entry["duration_seconds"] - entry["raw_duration_seconds"]
                if pad_sec > 0:
                    pad_frames = int(pad_sec * sample_rate)
                    out_wf.writeframes(silence_frame * pad_frames)

if __name__ == "__main__":
    manager = NarrationManager()
    res = manager.process_script(
        "examples/two-sum/05_narration_script.json",
        "output/two-sum-prototype"
    )
    print("Narration generation complete!")
    print(f"Total duration: {res['total_duration_seconds']}s ({res['total_frames']} frames @ 30fps)")
    for seg in res["segments"]:
        print(f" - [{seg['segment_id']}] {seg['start_seconds']}s -> {seg['end_seconds']}s ({seg['duration_frames']} frames)")
