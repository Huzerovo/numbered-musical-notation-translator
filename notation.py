#!/usr/bin/env python3
"""
A numbered musical notation translator
"""

import argparse

keymap = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
notemap = [
    "1",
    "#1",
    "2",
    "#2",
    "3",
    "4",
    "#4",
    "5",
    "#5",
    "6",
    "#6",
    "7",
]

flat_notemap = [
    "1",
    "b2",
    "2",
    "b3",
    "b4",
    "4",
    "b5",
    "5",
    "b6",
    "6",
    "b7",
    "b1",
]

sharp_notemap = [
    "#7",
    "#1",
    "2",
    "#2",
    "3",
    "#3",
    "#4",
    "5",
    "#5",
    "6",
    "#6",
    "7",
]


class HeaderError(RuntimeError):
    """
    Exception for invalid header format
    """


class NotationError(RuntimeError):
    """
    Exception for invalid note format
    """


class Node:
    """
    notation node
    """

    is_note: bool
    is_line_end: bool
    # **prefix** definitaion
    # prefix is a string before the Node
    # if there is a line: '1 2 ? 3?', it means there are four nodes:
    # - a note node **1**, with prefix that is a empty string
    # - a note node **2**, with prefix that contains a string ` ` (a space)
    # - a note node **3**, with prefix that contains a string ` ? `, the '?' is
    #   around with space
    # - a end node, with prefix that that contains string `?`
    prefix = ""


class NoteNode(Node):
    """
    desctipt a note node
    """

    pitch = 0
    # base should be in range (-2, 2)
    # base > 0 means the note has a higher tone than the key and should be
    # around with '[]'
    # base > 0 means the note has a lower tone than the key and should be
    # around with '()'
    base = 0

    def __init__(self, pitch: int, target: int):
        """
        **pitch**: pitch of the note
        **target**: pitch of the target key
        """
        self.is_note = True
        if not pitch in range(1, 12 * 5 + 1):
            raise NotationError(
                "pitch should be in range (1, 60), but get " + str(pitch)
            )
        self.pitch = pitch
        offset = pitch - target
        while offset < 0:
            self.base -= 1
            offset += 12
        while offset >= 12:
            self.base += 1
            offset -= 12

    def __str__(self) -> str:
        prefix = ""
        suffix = ""
        offset = self.base
        while offset < 0:
            prefix += "("
            suffix += ")"
            offset += 1
        while offset > 0:
            prefix += "["
            suffix += "]"
            offset -= 1

        return prefix + str(self.pitch) + suffix


class EndNode(Node):
    """
    descript a line end node
    """

    def __init__(self):
        self.is_note = False
        self.is_line_end = True

    def __str__(self):
        return "\n"


class Notation:
    """
    The main translater
    """

    title: str
    notation: list = []
    keep_key_signature = False

    def __init__(self):
        self._keymap = keymap
        self._notemap = notemap
        self._pitch_orig = 0
        self._pitch_target = 0
        # pitch_base is in range(-2, 2)
        self._pitch_base = 0

    def __str__(self) -> str:
        output = "{\n"
        output += "  keymap: " + str(self._keymap) + "\n"
        output += "  notemap: " + str(self._notemap) + "\n"
        output += "  origin pitch: " + str(self._pitch_orig) + "\n"
        output += "  target pitch: " + str(self._pitch_target) + "\n"
        output += "  title: " + self.title + "\n"
        output += "  notation:\n"
        output += "  " + str([str(x) for x in self.notation]) + "\n"
        output += "}"
        return output

    def _keymap_idx(self, key: str) -> int:
        try:
            idx = self._keymap.index(key.upper())
        except ValueError as e:
            raise NotationError("invalid key " + key) from e
        return idx

    def _notemap_idx(self, note: str) -> int:
        try:
            idx = self._notemap.index(note)
        except ValueError as e:
            raise NotationError("invalid note " + note) from e
        return idx

    def _key_signature(self) -> str:
        return "1=" + self._keymap[(self._pitch_target - 1) % 12]

    def set_notemap(self, new_notemap: list):
        """
        set notemap
        """
        self._notemap = new_notemap

    def _tone_to_pitch(self, tone: str) -> int:
        """
        get the pitch of a tone
        **tone**: a key that can include '()' or '[]'
        **return**: the pitch of the tone
        """
        base = 2
        key = ""

        # convert tone to a key
        # stack for detect closed "()" or "[]"
        st = []
        for c in tone:
            if c == "(":
                base -= 1
                st.append(c)
            elif c == "[":
                base += 1
                st.append(c)
            elif c == ")":
                if st.pop() != "(":
                    raise NotationError("invalid tone " + tone)
            elif c == "]":
                if st.pop() != "[":
                    raise NotationError("invalid tone " + tone)
            else:
                key = key + c

        if len(st) != 0:
            raise NotationError("invalid tone " + tone)

        idx = 12 * base + self._keymap_idx(key)
        return idx + 1

    def _note_to_pitch(self, note: str) -> int:
        """
        convert note to a pitch
        **note**: see *notemap*
        """
        if self._pitch_orig == 0:
            raise NotationError("origin pitch is unset")
        if note.startswith("b"):
            note = note.removeprefix("b")
            idx = self._notemap_idx(note)
            idx -= 1
        else:
            idx = self._notemap_idx(note)
        return self._pitch_orig + 12 * self._pitch_base + idx

    def _pitch_to_note(self, pitch: int) -> str:
        """
        convert pitch to a note
        """
        if self._pitch_target == 0:
            raise NotationError("target pitch is unset")
        if pitch < 0 or pitch > 12 * 5:
            raise NotationError("pitch out of range " + pitch)
        offset = pitch - self._pitch_target + 12 * self._pitch_base
        if offset < 0:
            offset += 12 * 2
        return self._notemap[offset % 12]

    def _generate_line(self, line: str) -> list:
        nt = []
        i = 0
        prefix = ""
        while i < len(line):
            c = line[i]
            if "1" <= c <= "7":
                pitch = self._note_to_pitch(c)
                note = NoteNode(pitch, self._pitch_target)
                note.prefix = prefix
                nt.append(note)
                prefix = ""
            elif c == "#":
                i += 1
                c = line[i]
                if not "1" <= c <= "7":
                    # if '#' is not a note, ignore it
                    prefix += "#"
                    continue
                if c == "7":
                    self._pitch_base += 1
                    note = NoteNode(
                        self._note_to_pitch("1"), self._pitch_target
                    )
                    self._pitch_base -= 1
                elif c == "3":
                    note = NoteNode(
                        self._note_to_pitch("4"), self._pitch_target
                    )
                else:
                    note = NoteNode(
                        self._note_to_pitch("#" + c), self._pitch_target
                    )
                note.prefix = prefix
                nt.append(note)
                prefix = ""
            elif c == "b":
                i += 1
                c = line[i]
                if not "1" <= c <= "7":
                    prefix += "b"
                    continue
                note = NoteNode(
                    self._note_to_pitch("b" + c), self._pitch_target
                )
                note.prefix = prefix
                nt.append(note)
                prefix = ""
            elif c in ("(", "]"):
                self._pitch_base -= 1
            elif c in (")", "["):
                self._pitch_base += 1
            elif c == "\n":
                node = EndNode()
                node.prefix = prefix
                nt.append(node)
                prefix = ""
            else:
                prefix += c
            i += 1
        return nt

    def translate(self, orig: str, target: str, ifile: str):
        """
        translate note to 'target'
        """
        with open(ifile, encoding="utf-8") as fd:
            # set title
            self.title = fd.readline().strip()
            if orig != 0:
                self._pitch_orig = self._tone_to_pitch(orig)
            # set target pitch
            self._pitch_target = self._tone_to_pitch(target)

            # translate notation
            nt: list = []
            for line in fd:
                # note signature line
                if line.startswith("1="):
                    if self._pitch_base != 0:
                        raise NotationError(
                            "there has a unclosed decoration before change "
                            + "signature at line "
                            + str(fd.tell())
                        )
                    key = line.removeprefix("1=").strip()
                    self._pitch_orig = self._tone_to_pitch(key)
                    if self.keep_key_signature:
                        node = EndNode()
                        node.prefix = "// origin key signature " + line.strip()
                        nt.append(node)
                # comment line
                elif line.startswith("//"):
                    node = EndNode()
                    node.prefix = line.strip()
                    nt.append(node)
                # note notation
                else:
                    nt.extend(self._generate_line(line))

            if self._pitch_base != 0:
                raise NotationError(
                    "incompleted notation, pitch_base should be 0 but get "
                    + str(self._pitch_base)
                )
            self.notation = nt

    def _note_decoration(self, st: list, node: Node) -> (str, str, list):
        prefix = ""
        suffix = ""
        while node.base < self._pitch_base:
            self._pitch_base -= 1
            if len(st) == 0:
                suffix += "("
                st.append("(")
            else:
                c = st.pop()
                if c == "[":
                    prefix += "]"
                elif c == "(":
                    suffix += "("
                    st.append(c)
                    st.append("(")
                else:
                    raise NotationError("stack contain " + c)
        while node.base > self._pitch_base:
            self._pitch_base += 1
            if len(st) == 0:
                suffix = "["
                st.append("[")
            else:
                c = st.pop()
                if c == "(":
                    prefix += ")"

                elif c == "[":
                    suffix = "["
                    st.append(c)
                    st.append("[")
                else:
                    raise NotationError("stack contain " + c)
        return prefix, suffix, st

    def print(self, ofile: str = None):
        """
        output a tone
        """
        st = []
        output = self.title + "\n" + self._key_signature() + "\n"
        for node in self.notation:
            if node.is_note:
                prefix, suffix, st = self._note_decoration(st, node)

                output += (
                    prefix
                    + node.prefix
                    + suffix
                    + self._pitch_to_note(node.pitch)
                )
            else:
                if node.is_line_end:
                    while len(st) > 0:
                        c = st.pop()
                        if c == "(":
                            self._pitch_base += 1
                            output += ")"
                        else:
                            self._pitch_base -= 1
                            output += "]"
                output += node.prefix + "\n"
        if ofile is None:
            print(output, end="")
        else:
            with open(ofile, "w", encoding="utf-8") as fd:
                fd.write(output)


def main():
    """
    main function
    """
    # base on C tone
    parser = argparse.ArgumentParser(
        description="A harmonica numbered musical notation tones translater",
        epilog="You can choose tone in " + str(keymap),
    )
    parser.add_argument(
        "--comment-key-signature",
        help="show origin key signature in comment line",
        action="store_true",
    )
    parser.add_argument(
        "--prefer",
        help="use falt note replace sharp note",
        choices={"flat", "sharp"},
    )
    parser.add_argument(
        "-o",
        "--orig-key",
        default="C",
        help="translate from this tone as default if there is not a key "
        + "signature",
    )
    parser.add_argument(
        "-t", "--target-key", help="translate to this tone", required=True
    )
    parser.add_argument(
        "input_file", help="the numbered musical notation text file"
    )
    parser.add_argument(
        "output_file",
        help="the output translated notation file",
        nargs="?",
        default=None,
    )
    args = parser.parse_args()

    sheet = Notation()
    if args.comment_key_signature:
        sheet.keep_key_signature = True
    sheet.translate(args.orig_key, args.target_key, args.input_file)

    if args.prefer == "flat":
        sheet.set_notemap(flat_notemap)
    elif args.prefer == "sharp":
        sheet.set_notemap(sharp_notemap)

    sheet.print(args.output_file)


if __name__ == "__main__":
    main()
