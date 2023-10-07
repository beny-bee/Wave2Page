import demucs.separate


class Splitter:

    def __init__(self, source_path):
        self.source_path = source_path

    def separate(self, filename):
        path = self.source_path + '/' + filename
        demucs.separate.main(["--mp3", "-n", "htdemucs_6s", path])
        print("Succesfully separated track: " + filename + ' - results in /separated/htdemucs_6s/')


if __name__ == "__main__":
    sp = Splitter(r'E:\MAI\ISP\Wave2Page\src\splitter\examples')
    sp.separate('audio_example.mp3')
