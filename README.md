# whisper.cpp-podlove-convert

Python script for converting whisper.cpp JSON transcripts to Podlove Web Player transcripts.

## Usage

Create a whisper.cpp JSON transcript file, e.g.:

```command
$ ./main -m models/ggml-large-v1.bin -l de --output-json my_file.wav
```

Convert it to Podlove Web Player JSON:

```command
$ ./cpp_podlove_convert.py -d my_file.wav.json my_file.podlove.json
```

Copy this file to your website and configure Podlove Web Player to use this transcript:

```javascript
"transcripts": "my_file.podlove.json"
```

See `-h` / `--help` for additional arguments:

```command
$ ./cpp_podlove_convert.py --help
```
