from diarization import diarization
from pyannote.audio import Pipeline

if __name__ == '__main__':

    with open("diarization_output-1707215030.613478.rttm", "r") as file:
        data = file.readlines()

