header = """The following list contains all pentatonic (5 note) scales that meet the following criteria:
  * Made up of minor 2nd, major 2nd, minor 3rd or 3rd intervals
  * Do not have two consecutive minor 2nd intervals
This Results in 25 unique interval patterns, or scale groups, each from which five modes can be constructed, for
a total of 125 different scales. The scale group number is arbitrary, but scales within the same scale group are 
modes of each other. For example, the western major and minor pentatonic scales come from scale group 25, 
Modes 3 and 2 respectively. Scale group 11 is usually referred to as the Japanese Hirajoshi scale, which contains 
the Japanese Akebono, In and Iwato scales, while group 6 contains the Insen scale and its modes.
We represent each scale as numbers of semitones above the root, always starting with zero (the root note)

Some notable scales:
    0, 2, 4, 7, 9: Major Pentatonic
    0, 3, 5, 7, 10: Minor Pentatonic
    0, 4, 5, 7, 10: Dominant 7th
    0, 2, 4, 7, 10: Dominant 7th Sus2
    0, 2, 4, 7, 11: Major 7th Sus2
    0, 4, 5, 7, 11: Major 7th 4th
    0, 2, 4, 6, 9: Major Sharp 4th
    0, 3, 5, 7, 9: Minor 6th
    0, 2, 5, 7, 10: Egyptian scale	
    0, 2, 3, 7, 8: Hirajoshi, Akebono Scale
    0, 1, 5, 7, 8: In Scale
    0, 1, 5, 7, 10: Insen Scale
    0, 1, 5, 6, 10: Iwato Scale

Semitones
    A list of all five notes, as semitones above the root.
Scale Group
    A number that identifies which scales comes from the same group. Each scale in a group can be consider
    to be a mode of the other scales within the same group.
Mode Number
    The number from 1 to 5 representing an inversion, or mode, of the scale within its group.
    The number is arbitrary and does not hold any significance between different groups
Flat Representation
    Lists the intervals in the scale using flats
Sharp Representation
    Lists the intervals in the scale using sharps
Features
    Identifies scales which encompass major and minor triads, as well as minor 7th, dominant 7th and major 7ths	
    
"""


def bits(input):
    return bin(input).count("1")


def get_modes(scale):
    output = []
    for i in range(len(scale)):
        output.append(scale)
        offset = scale[1]
        mode = tuple(s - offset for s in scale)
        mode = mode[1:] + (mode[0] + 12,)
        scale = mode
    return output


def to_tuple(val):
    s = bin(val)[2:]
    output = []
    for i in range(len(s)):
        if s[i] == '1':
            output.append(i)
    return tuple(output)


def intervals(tpl):
    output = []
    tpl = tpl + (12,)
    for i in range(len(tpl) - 1):
        interval = tpl[i + 1] - tpl[i]
        output.append(interval)
    return output


def is_squished(tpl):
    v = intervals(tpl)
    if v[0] == 1 and v[1] == 1:
        return True
    if v[1] == 1 and v[2] == 1:
        return True
    if v[2] == 1 and v[3] == 1:
        return True
    if v[3] == 1 and v[4] == 1:
        return True
    if v[4] == 1 and v[0] == 1:
        return True
    return False


def is_large(tpl):
    v = intervals(tpl)
    return any(x > 4 for x in v)


def generate():
    known = []
    for i in range(2 ** 12):
        if bits(i) != 5 or (i % 2) != 1:
            continue

        tpl = to_tuple(i)
        if not any(mode in known for mode in get_modes(tpl)):
            known.append(tpl)

    return known


def filter_scales(known):
    good = []
    for tpl in known:
        if is_squished(tpl):
            # two half steps in succession
            continue
        if is_large(tpl):
            continue

        good.append(tpl)
    return good


def note_sequence(scale):
    # two octave run, up then down
    reverse = scale[::-1]
    reverse = (12,) + reverse[:-1]
    return scale + tuple(s + 12 for s in scale) + tuple(s + 12 for s in reverse) + reverse + (0,)


def midi(scale, root=60, include_bass=True):
    from midiutil import MIDIFile

    track = 0
    channel = 0
    time = 0  # In beats
    duration = 1  # In beats
    tempo = 130  # In BPM
    volume = 120  # 0-127

    for mode in get_modes(scale):
        MyMIDI = MIDIFile(1)
        MyMIDI.addTempo(track, time, tempo)
        sequence = note_sequence(mode)

        if include_bass:
            MyMIDI.addNote(track, channel, root - 12, time, duration * 5, volume)
            MyMIDI.addNote(track, channel, root - 12, time + 5, duration * 5, volume)
            MyMIDI.addNote(track, channel, root - 12, time + 10, duration * 5, volume)
            MyMIDI.addNote(track, channel, root - 12, time + 15, duration * 5, volume)
            MyMIDI.addNote(track, channel, root - 12, time + 20, duration, volume)

        for i, pitch in enumerate(sequence):
            MyMIDI.addNote(track, channel, root + pitch, time + i + 0.02, duration, volume)

        filename = str(mode)[1:-1]
        out_file = filename + ".mid"
        with open(out_file, "wb") as output_file:
            MyMIDI.writeFile(output_file)


def write_data(scale, mode_id):
    output = []
    for mode_num, mode in enumerate(get_modes(scale)):
        scale_str = ""
        intervals = get_intervals(mode)
        scale_str += ", ".join(str(x) for x in mode).ljust(15)
        scale_str += ' | '
        scale_str += str(mode_id).ljust(12)
        scale_str += ' | '
        scale_str += str(mode_num + 1).ljust(12)
        scale_str += ' | '
        scale_str += ", ".join(intervals[0]).ljust(18)
        scale_str += ' | '
        scale_str += ", ".join(intervals[1]).ljust(18)
        scale_str += ' | '
        features = []
        if 3 in mode and 7 in mode and 10 in mode:
            features.append("Min7")
        elif 3 in mode and 7 in mode and 11 in mode:
            features.append("MinMaj7")
        elif 4 in mode and 7 in mode and 10 in mode:
            features.append("Dom7")
        elif 4 in mode and 7 in mode and 11 in mode:
            features.append("Maj7")
        elif 3 in mode and 7 in mode:
            features.append("Min")
        elif 4 in mode and 7 in mode:
            features.append("Maj")

        if len(features) > 0:
            scale_str += features[0]
        output.append(scale_str)
    return output


def write_header():
    output = []
    header = 'Semitones'.ljust(15)
    header += ' | '
    header += 'Scale Group'.ljust(12)
    header += ' | '
    header += 'Mode Number'.ljust(12)
    header += ' | '
    header += 'Flat Repr.'.ljust(18)
    header += ' | '
    header += 'Sharp Repr.'.ljust(18)
    header += ' | '
    header += 'Features'.ljust(18)
    output.append(header)
    return output


def get_intervals(scale):
    flats = []
    sharps = []

    flats.append('1')
    sharps.append('1')

    if 1 in scale:
        flats.append('b2')
        sharps.append('#1')
    if 2 in scale:
        flats.append('2')
        sharps.append('2')
    if 3 in scale:
        flats.append('b3')
        sharps.append('#2')
    if 4 in scale:
        flats.append('3')
        sharps.append('3')
    if 5 in scale:
        flats.append('4')
        sharps.append('4')
    if 6 in scale:
        flats.append('b5')
        sharps.append('#4')
    if 7 in scale:
        flats.append('5')
        sharps.append('5')
    if 8 in scale:
        flats.append('b6')
        sharps.append('#5')
    if 9 in scale:
        flats.append('6')
        sharps.append('6')
    if 10 in scale:
        flats.append('b7')
        sharps.append('#6')
    if 11 in scale:
        flats.append('7')
        sharps.append('7')

    return flats, sharps


def main():
    known = generate()
    good_scales = filter_scales(known)
    data = []
    for i, scale in enumerate(good_scales):
        data.extend(write_data(scale, i + 1))
        midi(scale)

    sorter = lambda line: tuple(int(i) for i in line.split('|')[0].split(','))
    data = write_header() + sorted(data, key=sorter)
    with open('scale_info.txt', "w") as f:
        f.write(header)
        f.writelines((x + '\n' for x in data))


main()
