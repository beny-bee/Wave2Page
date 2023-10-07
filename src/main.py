from midi2Sheet import midi2Sheet

def main():   
    # Mock mp3 to midi
    midiPath = "midi2Sheet/SampleMIDI.mid"
    sheetName = "FirstMusicSheets"
    midi2Sheet.midi2Sheet(midiPath, sheetName)

if __name__ == '__main__':
    main()