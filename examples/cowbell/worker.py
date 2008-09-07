import eyeD3
from cowbell import Cowbell
import echonest.audio as audio


def write_tags(path, metadata):
    tag = eyeD3.Tag()
    tag.link(path)
    tag.header.setVersion(eyeD3.ID3_V2_3)
    if metadata.has_key('artist'):
        tag.setArtist(metadata['artist'])
    if metadata.has_key('release'):
        tag.setAlbum(metadata['release'])
    if metadata.has_key('title'):
        tag.setTitle(metadata['title'])
    else:
        tag.setTitle('Unknown song')
    tag.update()



def main( inputFilename, outputFilename, cowbellIntensity, walkenIntensity ) :

    # Upload track for analysis.
    print 'uploading audio file...'
    track = audio.AudioTrack(inputFilename)

    # Get beats.
    print 'getting beats...'
    num_beats = len(track.beats.firstChild.childNodes[3].childNodes)
    beats = []
    for i in range(num_beats):
        start = float(track.beats.firstChild.childNodes[3].childNodes[i].firstChild.data)
        beats.append({'start': start})
        beats[i - 1]['duration'] = start - beats[i - 1]['start']
    beats[num_beats - 1]['duration'] = beats[num_beats - 2]['duration']

    # Get sections.
    print 'getting sections...'
    sections = []
    for node in track.sections.firstChild.childNodes[3].childNodes:
        sections.append(float(node.getAttribute('start')))
            
    # Get metadata.
    print 'getting metadata...'
    metadata = {}
    for node in track.metadata.firstChild.childNodes[3].childNodes:
        metadata[node.nodeName] = node.firstChild.data

    # Add the cowbells.
    print 'cowbelling...'
    Cowbell(inputFilename, beats, sections).run(self.cowbell_intensity, self.walken_intensity, outputFilename)            

    # Finalize output file.
    print 'finalizing output file...'
    write_tags(outputFilename, metadata)



if __name__ == '__main__':
    import sys
    main(sys.argv[-4], sys.argv[-3], sys.argv[-2], sys.argv[-1])
