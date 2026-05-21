"""ac's smb utility — GUI port of SMB Utility 1.08 (M.K.S).

Upstream readme:
https://github.com/Maseya/SMB-Utility/blob/master/src/misc/readme.en-US.txt
Stdlib only (tkinter). Do not bundle or distribute copyrighted game ROMs.
"""

from __future__ import annotations

import os
import tkinter as tk
from dataclasses import dataclass, field
from tkinter import filedialog, messagebox, scrolledtext, ttk

UPSTREAM_README_URL = (
    "https://github.com/Maseya/SMB-Utility/blob/master/src/misc/readme.en-US.txt"
)
README_EN_US = """\
SMB Utility ver.1.08

§ 1 Summary
SMB Utility is an application for Windows (R) to create an original map of Super
Mario Bros. (TM). SMB Utility and its authors have nothing to do with Nintendo
(R), the developer of Super Mario Bros. (TM).

§ 2 File description
 smbutil.exe: Executable file of SMB Utility.
 smbutil.ini: Initialization file of SMB Utility.
 readme.txt: Current open file.
 howto.htm: Usage hints are written.
 history.txt: This is the version upgrade history of SMB Utility.
 delreg.exe: A program that deletes SMB Utility's registry key (setting) and
    executes it when uninstalling.
 sample /: IPS file for sample level created by SMK Utility by M.K.H.

§ 3 license
SMB Utility (hereinafter referred to as this software) is freeware. The
copyright of this software belongs to M.K.S (hereinafter referred to as the
author). Reprinting / distribution of this software can be freely carried out
only for non - commercial use, it is strictly prohibited to bundle the game ROM
file. In addition, the author is not obligated to compensate for any damage
caused by using this software.

§ 4 Contribution
SWR: New code maintainer.
Multi-6502 CPU (.asm code) emulator by Neil Bradley (neil@synthcom.com)
Mr. Chezzman 1 and Waiwai came to translate English translation of 1.00
    International beta 3.
In 1.08 International translation, I referred to the item of What's added in ISD
    SMB Util? In ReadMe.txt included in ISD SMB Util created by Insectduel.
1.08 I translate SMB Utility English Version 1.07 created by Mirracle MXX in
    English into English translation.

§ 5 Other
Company names and product names that appear in this text are trademarks or
    registered trademarks of each company.
"""

PYTHON_PORT_NOTE = """\
--- ac's smb utility (this program) ---
Python/tkinter port with objlib/roommng seek logic and opcode tables from SMB Utility 1.08.
HUD text, object list, map header bytes, and per-object ROM patches are implemented.
6502 in-emulator test play is still not wired.
"""

PROGRAM_NAME = "SMB Utility"
APP_VERSION = "1.08 (Python port 0.3)"

INES_MAGIC = b"NES\x1a"
INES_HEADER_SIZE = 16

TEXT_OFFSETS_PRG = {
    "MARIO String": 0x0765,
    "LUIGI String": 0x07FD,
    "WORLD String": 0x076D,
    "TIME String": 0x0774,
}
TEXT_LENGTHS = {
    "MARIO String": 5,
    "LUIGI String": 5,
    "WORLD String": 5,
    "TIME String": 4,
}
LEVEL_HEADER_START_PRG = 0x1CCC

# --- PRG addresses (roommng.h / objlib.h) ---
SMB_WORLD_SETTING = 0x9CB4
SMB_AREA_SETTING = 0x9CBC
SMB_BADGUYS_ADDRESS_HEAD = 0x9CE0
SMB_BADGUYS_ADDRESS_LOW = 0x9CE4
SMB_BADGUYS_ADDRESS_HIGH = 0x9D06
SMB_MAP_ADDRESS_HEAD = 0x9D28
SMB_MAP_ADDRESS_LOW = 0x9D2C
SMB_MAP_ADDRESS_HIGH = 0x9D4E
SMB_OBJECT_START_ADDRESS = 0x9D70
SMB_OBJECT_END_ADDRESS = 0xAEDC
SMB_NUM_ADDRESSDATA = 34
SMB_NUM_AREAS = 36

SMB_STRING_NAMES = tuple(f"String {i:02d}" for i in range(1, 21))

# Map type 0x0B basic blocks (objdata.c InitSmbMapObjectInfo0B indices)
MAP_BASIC_BLOCKS = (
    "Ground", "Block/Bush", "Block/Tree", "Block/Cloud", "Block?",
    "Pipe/H", "Pipe/V", "Question", "Metal", "Coin",
    "Ice", "Wood", "Bridge", "Coral", "Blank",
    "Blank",
)

MAP_OBJ_B = (
    "Ground", "Block/Bush", "Block/Tree", "Block/Cloud", "Block?",
    "Pipe/H", "Pipe/V", "Question", "Metal", "Coin",
    "Ice", "Wood", "Bridge", "Coral", "Page break (0x0D)",
    "Vertical pipe", "Horizontal pipe", "Vertical pipe (alt)",
    "Len pipe H+1", "Len pipe V+1", "Len blocks+1", "Len blocks+1",
    "Len blocks+1", "Len blocks+1", "Len blocks+1", "Len blocks+1",
    "Len blocks+1", "Len blocks+1",
)

MAP_OBJ_C = (
    "Len blocks+1 (C0)", "Len blocks+1 (C1)", "Len blocks+1 (C2)",
    "Len blocks+1 (C3)", "Len blocks+1 (C4)", "Len blocks+1 (C5)",
    "Len blocks+1 (C6)", "Len blocks+1 (C7)",
)

MAP_OBJ_D = (
    "Set page", "D40", "D41", "D42", "D43", "D44", "D45", "D46", "D47",
    "D48", "D49", "D4A", "D4B", "D4C", "D4D", "D4E", "D4F",
)

MAP_HEAD_TIME = ("400", "300", "200", "No limit")
MAP_HEAD_POSITION = (
    "Default", "High", "Very high", "Low",
    "Default", "Default", "Default", "Default",
)
MAP_HEAD_BACKCOLOR = (
    "Black", "Blue", "Red", "Green", "Indigo", "Gray", "Gray", "White",
)
MAP_HEAD_MAPTYPE = ("Overworld", "Underground", "Castle", "Underwater")
MAP_HEAD_VIEW = ("Scroll", "No scroll", "Alt", "Alt2")

# Bad-guy object IDs (byte1 & 0x3F) — smbBadGuysInfo table order
BADGUYS_NAMES: tuple[str, ...] = (
    "Goomba", "Green Koopa", "Red Koopa", "Piranha Plant", "Buzzy Beetle",
    "Cheep Cheep", "Cheep Cheep (alt)", "Blooper", "Muncher", "Lakitu",
    "Spiny", "Empty", "Hammer Bro", "Empty", "Firebar",
    "Firebar (alt)", "Black Cheep", "Thwomp", "Boo", "Empty",
    "Hard mode flag", "Power-up", "1-Up", "Coin", "Empty",
    "Empty", "Empty", "Empty", "Lift", "Empty",
    "Empty", "Empty", "Empty", "Empty", "Empty",
    "Empty", "Empty", "Bullet Bill", "Hammer Bro (alt)", "Podoboo",
    "Podoboo (alt)", "Empty", "Empty", "Empty", "Empty",
    "Empty", "Empty", "Empty", "Empty", "Empty",
    "Empty", "Empty", "Empty", "Empty", "Empty",
    "Empty", "Lift (alt)", "Lift (alt)", "Lift (alt)", "Lift (alt)",
    "Lift (alt)", "Lift (alt)", "Lift (alt)", "Lift (alt)",
)

SMB_CHAR_TO_BYTE: dict[str, int] = {str(d): d for d in range(10)}
for _i in range(26):
    SMB_CHAR_TO_BYTE[chr(ord("A") + _i)] = 0x0A + _i
SMB_CHAR_TO_BYTE.update({" ": 0x24, "-": 0x28, "×": 0x29, "!": 0x2B, ".": 0xAF, "©": 0xCF})
SMB_BYTE_TO_CHAR: dict[int, str] = {v: k for k, v in SMB_CHAR_TO_BYTE.items()}
SMB_PAD_BYTE = 0x24

PAGEOBJECT_NO = 0
PAGEOBJECT_NEXTPAGEFLAG = 1
PAGEOBJECT_SETPAGE = 2


def smb_encode(text: str, length: int) -> bytes:
    out = bytearray()
    for ch in text.upper()[:length]:
        out.append(SMB_CHAR_TO_BYTE.get(ch, SMB_PAD_BYTE))
    while len(out) < length:
        out.append(SMB_PAD_BYTE)
    return bytes(out)


def smb_decode(raw: bytes) -> str:
    return "".join(SMB_BYTE_TO_CHAR.get(b, ".") for b in raw).rstrip()


def prg_to_file_offset(prg_addr: int, has_ines: bool = True) -> int:
    base = INES_HEADER_SIZE if has_ines else 0
    if prg_addr < 0x8000:
        return base + prg_addr
    return base + 0x4000 + (prg_addr - 0x8000)


@dataclass
class ObjectSeekInfo:
    offset: int = 0
    index: int = 0
    page: int = 0
    obj_len: int = 2
    prev_page_com: bool = False


@dataclass
class ParsedObject:
    index: int
    page: int
    x: int
    y: int
    raw: bytes
    kind: str
    label: str
    prg_offset: int


class SMBRomEngine:
    """Port of objlib.c + roommng.c address/seek helpers."""

    def __init__(self, rom: bytearray) -> None:
        self.rom = rom
        self.has_ines = len(rom) >= 4 and bytes(rom[:4]) == INES_MAGIC
        self.length_valid = True
        self.world_data = bytearray(8)
        self.area_data = bytearray(SMB_NUM_AREAS)
        self.addr_head_map = bytearray(4)
        self.addr_head_badguys = bytearray(4)
        self.addr_data_map: list[int] = [0] * SMB_NUM_ADDRESSDATA
        self.addr_data_badguys: list[int] = [0] * SMB_NUM_ADDRESSDATA
        self.reload_tables()

    def _read_prg(self, prg_addr: int, size: int = 1) -> bytes:
        start = prg_to_file_offset(prg_addr, self.has_ines)
        return bytes(self.rom[start : start + size])

    def _write_prg(self, prg_addr: int, data: bytes) -> None:
        start = prg_to_file_offset(prg_addr, self.has_ines)
        for i, b in enumerate(data):
            self.rom[start + i] = b

    def reload_tables(self) -> None:
        self.world_data[:] = self._read_prg(SMB_WORLD_SETTING, 8)
        self.area_data[:] = self._read_prg(SMB_AREA_SETTING, SMB_NUM_AREAS)
        self.addr_head_map[:] = self._read_prg(SMB_MAP_ADDRESS_HEAD, 4)
        self.addr_head_badguys[:] = self._read_prg(SMB_BADGUYS_ADDRESS_HEAD, 4)
        for i in range(SMB_NUM_ADDRESSDATA):
            lo = prg_to_file_offset(SMB_MAP_ADDRESS_LOW + i, self.has_ines)
            hi = prg_to_file_offset(SMB_MAP_ADDRESS_HIGH + i, self.has_ines)
            self.addr_data_map[i] = self.rom[lo] | (self.rom[hi] << 8)
            lo = prg_to_file_offset(SMB_BADGUYS_ADDRESS_LOW + i, self.has_ines)
            hi = prg_to_file_offset(SMB_BADGUYS_ADDRESS_HIGH + i, self.has_ines)
            self.addr_data_badguys[i] = self.rom[lo] | (self.rom[hi] << 8)

    def save_tables(self) -> None:
        self._write_prg(SMB_WORLD_SETTING, bytes(self.world_data))
        self._write_prg(SMB_AREA_SETTING, bytes(self.area_data))
        self._write_prg(SMB_MAP_ADDRESS_HEAD, bytes(self.addr_head_map))
        self._write_prg(SMB_BADGUYS_ADDRESS_HEAD, bytes(self.addr_head_badguys))
        for i in range(SMB_NUM_ADDRESSDATA):
            w = self.addr_data_map[i]
            self.rom[prg_to_file_offset(SMB_MAP_ADDRESS_LOW + i, self.has_ines)] = w & 0xFF
            self.rom[prg_to_file_offset(SMB_MAP_ADDRESS_HIGH + i, self.has_ines)] = (w >> 8) & 0xFF
            w = self.addr_data_badguys[i]
            self.rom[prg_to_file_offset(SMB_BADGUYS_ADDRESS_LOW + i, self.has_ines)] = w & 0xFF
            self.rom[prg_to_file_offset(SMB_BADGUYS_ADDRESS_HIGH + i, self.has_ines)] = (w >> 8) & 0xFF

    @staticmethod
    def make_room_id(area_byte: int) -> int:
        return area_byte & 0x7F

    def room_id_for_area(self, area_index: int) -> int:
        if 0 <= area_index < SMB_NUM_AREAS:
            return self.make_room_id(self.area_data[area_index])
        return 0

    def get_map_address(self, room_id: int) -> int:
        head = self.addr_head_map[(room_id >> 5) & 3]
        return self.addr_data_map[head + (room_id & 0x1F)]

    def get_badguys_address(self, room_id: int) -> int:
        head = self.addr_head_badguys[(room_id >> 5) & 3]
        return self.addr_data_badguys[head + (room_id & 0x1F)]

    def map_data_length(self, room_id: int) -> int:
        start = self.get_map_address(room_id)
        nxt = SMB_OBJECT_END_ADDRESS
        for addr in self.addr_data_map + self.addr_data_badguys:
            if start < addr < nxt:
                nxt = addr
        return max(0, nxt - start - 2)

    def badguys_data_length(self, room_id: int) -> int:
        start = self.get_badguys_address(room_id)
        nxt = SMB_OBJECT_END_ADDRESS
        for addr in self.addr_data_badguys + self.addr_data_map:
            if start < addr < nxt:
                nxt = addr
        return max(0, nxt - start)

    @staticmethod
    def badguys_entry_len(buf: bytes) -> int:
        return 3 if len(buf) >= 1 and (buf[0] & 0x0F) == 0x0E else 2

    @staticmethod
    def badguys_y_delta(enemy_id: int) -> int:
        if enemy_id in (0x21, 0x22, 0x23, 0x24, 0x25, 0x28, 0x29, 0x2A, 0x2B, 0x2C, 0x2D):
            return 0
        if enemy_id in (0x37, 0x38, 0x39, 0x3A, 0x3B, 0x3C, 0x3D, 0x3E, 0x3F):
            return -2
        return -1

    @staticmethod
    def badguys_fixed_y(enemy_id: int) -> int | None:
        if enemy_id == 0x54:
            return 0x09
        if enemy_id in (0x56, 0x57):
            return 0x0A
        if enemy_id in (0x58, 0x59):
            return 0x06
        if enemy_id in (0x5A, 0x5B, 0x5C, 0x5D):
            return 0x0A
        if enemy_id in (0x5E, 0x5F):
            return 0x06
        return None

    def badguys_x_pos(self, buf: bytes) -> int:
        if (buf[0] & 0x0F) == 0x0E:
            return (buf[0] >> 4) & 0x0F
        eid = buf[1] & 0x3F
        return ((buf[0] >> 4) & 0x0F) + (1 if eid in (0x39, 0x3A, 0x44, 0x45) else 0)

    def badguys_y_pos(self, buf: bytes) -> int:
        low = buf[0] & 0x0F
        if low == 0x0E:
            return 0x0E
        if low == 0x0F:
            return 0x0F
        eid = buf[1] & 0x3F
        fixed = self.badguys_fixed_y(eid)
        if fixed is not None:
            return fixed
        return low + self.badguys_y_delta(eid)

    @staticmethod
    def map_x_pos(buf: bytes) -> int:
        return (buf[0] >> 4) & 0x0F

    @staticmethod
    def map_y_pos(buf: bytes) -> int:
        return buf[0] & 0x0F

    def format_map_string(self, buf: bytes) -> str:
        if len(buf) < 2:
            return "?"
        low, b1 = buf[0] & 0x0F, buf[1]
        if low == 0x0C:
            idx = (b1 >> 4) & 7
            name = MAP_OBJ_C[idx] if idx < len(MAP_OBJ_C) else "?"
            return f"Len {(b1 & 0x0F) + 1} {name}"
        if low == 0x0D:
            if not (b1 & 0x40):
                return f"Set page:{b1 & 0x3F:02d}"
            if (b1 & 0x70) == 0x40:
                idx = (b1 & 0x0F) + 1
                return MAP_OBJ_D[idx] if idx < len(MAP_OBJ_D) else "?"
            return "Unknown D"
        if low == 0x0E:
            if b1 & 0x40:
                idx = b1 & 7
                return f"Back {MAP_HEAD_BACKCOLOR[idx] if idx < 8 else idx}"
            v = (b1 >> 4) & 3
            bb = b1 & 0x0F
            blk = MAP_BASIC_BLOCKS[bb] if bb < len(MAP_BASIC_BLOCKS) else f"blk{bb}"
            return f"View {MAP_HEAD_VIEW[v] if v < 4 else v} / {blk}"
        if low == 0x0F:
            sub = (b1 >> 4) & 7
            if sub == 0:
                return "Rope"
            if sub in (1, 4, 5):
                fi = sub if sub == 1 else sub + 1
                name = MAP_OBJ_B[0x10 + ((b1 >> 4) & 7)] if 0x10 + ((b1 >> 4) & 7) < len(MAP_OBJ_B) else "F"
                return f"Len {(b1 & 0x0F) + 1} {name}"
            if sub == 2:
                h = b1 & 0x0F
                return f"Castle height {0x0B - h + 1}" if h <= 0x0B else "Crash"
            if sub == 3:
                return "Stairs"
            return "None"
        if not (b1 & 0x70):
            idx = b1 & 0x0F
            return MAP_OBJ_B[idx] if idx < len(MAP_OBJ_B) else f"B{idx:02X}"
        if (b1 & 0x70) != 0x70:
            idx = 0x0F + ((b1 >> 4) & 7)
            name = MAP_OBJ_B[idx] if idx < len(MAP_OBJ_B) else "?"
            return f"Len {(b1 & 0x0F) + 1} {name}"
        if b1 & 0x08:
            return f"Len {(b1 & 7) + 1} Vertical pipe"
        return f"Len {(b1 & 0x0F) + 1} Horizontal pipe"

    def format_badguys_string(self, buf: bytes) -> str:
        if not buf:
            return "?"
        low = buf[0] & 0x0F
        if low == 0x0E and len(buf) >= 3:
            attrs = MAP_HEAD_MAPTYPE
            attr = attrs[(buf[1] >> 5) & 3] if ((buf[1] >> 5) & 3) < 4 else "?"
            return f"Room {buf[1] & 0x7F:02X} {attr} page {((buf[2] >> 5) & 7) + 1} area {buf[2] & 0x1F}"
        if low == 0x0F:
            return f"Page command → {buf[1] & 0x3F}"
        eid = buf[1] & 0x3F
        name = BADGUYS_NAMES[eid] if eid < len(BADGUYS_NAMES) else f"Enemy {eid:02X}"
        hard = " (hard)" if (buf[1] & 0x40) and low not in (0x0E, 0x0F) else ""
        return name + hard

    def _badguys_set_page(self, info: ObjectSeekInfo, b0: int, b1: int) -> None:
        if (b1 & 0x80) and not info.prev_page_com:
            info.page += 1
        elif (b0 & 0x0F) == 0x0F:
            info.page = b1 & 0x3F
            info.prev_page_com = True
        if (b0 & 0x0F) != 0x0F:
            info.prev_page_com = False

    def _map_set_page(self, info: ObjectSeekInfo, b0: int, b1: int) -> None:
        if b1 & 0x80:
            info.page += 1
        elif (b0 & 0x0F) == 0x0D and not (b1 & 0x40):
            info.page = b1 & 0x3F

    def iter_badguys(self, room_id: int) -> list[ParsedObject]:
        base = self.get_badguys_address(room_id)
        length = self.badguys_data_length(room_id)
        off = 0
        info = ObjectSeekInfo()
        out: list[ParsedObject] = []
        while off < length:
            fo = prg_to_file_offset(base + off, self.has_ines)
            raw = bytes(self.rom[fo : fo + 3])
            if raw[0] == 0xFF:
                break
            olen = self.badguys_entry_len(raw)
            raw = raw[:olen]
            self._badguys_set_page(info, raw[0], raw[1])
            out.append(
                ParsedObject(
                    index=len(out),
                    page=info.page,
                    x=self.badguys_x_pos(raw),
                    y=self.badguys_y_pos(raw),
                    raw=raw,
                    kind="badguys",
                    label=self.format_badguys_string(raw),
                    prg_offset=base + off,
                )
            )
            if self.length_valid and off + olen > length:
                break
            off += olen
            info.offset = off
            if off > 0xFF:
                break
        return out

    def iter_map(self, room_id: int) -> list[ParsedObject]:
        base = self.get_map_address(room_id)
        length = self.map_data_length(room_id)
        off = 0
        info = ObjectSeekInfo()
        out: list[ParsedObject] = []
        while off < length:
            fo = prg_to_file_offset(base + 2 + off, self.has_ines)
            raw = bytes(self.rom[fo : fo + 2])
            if raw[0] == 0xFD:
                break
            self._map_set_page(info, raw[0], raw[1])
            out.append(
                ParsedObject(
                    index=len(out),
                    page=info.page,
                    x=self.map_x_pos(raw),
                    y=self.map_y_pos(raw),
                    raw=raw,
                    kind="map",
                    label=self.format_map_string(raw),
                    prg_offset=base + 2 + off,
                )
            )
            if self.length_valid and off + 2 > length:
                break
            off += 2
            info.offset = off
            if off > 0xFF:
                break
        return out

    def get_map_header(self, room_id: int) -> bytes:
        return self._read_prg(self.get_map_address(room_id), 2)

    def set_map_header(self, room_id: int, header: bytes) -> None:
        if len(header) >= 2:
            self._write_prg(self.get_map_address(room_id), header[:2])

    def write_object_bytes(self, prg_offset: int, data: bytes) -> None:
        self._write_prg(prg_offset, data)


class SMBUtility:
    APP_TITLE = f"{PROGRAM_NAME} {APP_VERSION}"

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(self.APP_TITLE)
        self.root.geometry("1100x720")
        self.root.minsize(900, 600)

        self.bg_color = "#000000"
        self.text_color = "#3399FF"
        self.accent_blue = "#002244"
        self.field_bg = "#001122"
        self.muted = "#6688aa"
        self.canvas_bg = "#101820"

        self.root.configure(bg=self.bg_color)

        self.rom_data: bytearray | None = None
        self.rom_path = ""
        self.rom_core: SMBRomEngine | None = None
        self.parsed_objects: list[ParsedObject] = []
        self.selected_obj_index = 0
        self.room_id_var = tk.IntVar(value=0)
        self.data_changed = False
        self.edit_mode = "map"
        self.world_var = tk.IntVar(value=1)
        self.area_var = tk.IntVar(value=1)
        self.page_var = tk.IntVar(value=0)
        self.show_toolbar = tk.BooleanVar(value=True)
        self.show_statusbar = tk.BooleanVar(value=True)
        self.show_logview = tk.BooleanVar(value=True)
        self.msg_on_save = tk.BooleanVar(value=True)

        self.notebook: ttk.Notebook | None = None
        self.tab_index: dict[str, int] = {}
        self.status_var = tk.StringVar(value="Ready.")
        self.log_widget: scrolledtext.ScrolledText | None = None
        self.text_entries: dict[str, tk.Entry] = {}
        self.toolbar_frame: tk.Frame | None = None
        self.log_frame: tk.Frame | None = None
        self.status_frame: tk.Frame | None = None
        self.map_canvas: tk.Canvas | None = None
        self.emu_canvas: tk.Canvas | None = None
        self.obj_tree: ttk.Treeview | None = None
        self.obj_bin_var = tk.StringVar(value="")
        self.obj_page_var = tk.StringVar(value="0")
        self.obj_x_var = tk.StringVar(value="0")
        self.obj_y_var = tk.StringVar(value="0")
        self.obj_type_var = tk.StringVar(value="")
        self.map_head_vars: dict[str, tk.StringVar] = {}
        self.rom_status_label: tk.Label | None = None

        self.setup_styles()
        self.create_menu()
        self.create_toolbar()
        self.create_main_layout()
        self._log("SMB Utility GUI initialized.")
        self._refresh_ui_state()

    def setup_styles(self) -> None:
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        self.style.configure(
            "TNotebook.Tab",
            background=self.accent_blue,
            foreground=self.text_color,
            bordercolor=self.bg_color,
            padding=(8, 4),
        )
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", self.text_color)],
            foreground=[("selected", self.bg_color)],
        )
        self.style.configure(
            "Treeview",
            background=self.field_bg,
            foreground=self.text_color,
            fieldbackground=self.field_bg,
            borderwidth=0,
        )
        self.style.configure(
            "Treeview.Heading",
            background=self.accent_blue,
            foreground=self.text_color,
        )

    def _menu(self, parent: tk.Menu) -> tk.Menu:
        return tk.Menu(
            parent,
            tearoff=0,
            bg=self.accent_blue,
            fg=self.text_color,
            activebackground=self.text_color,
            activeforeground=self.bg_color,
        )

    def create_menu(self) -> None:
        bar = tk.Menu(
            self.root,
            bg=self.accent_blue,
            fg=self.text_color,
            activebackground=self.text_color,
            activeforeground=self.bg_color,
        )

        file_m = self._menu(bar)
        file_m.add_command(label="Open...", command=self.open_rom, accelerator="Ctrl+O")
        file_m.add_command(label="Save", command=self.save_rom, accelerator="Ctrl+S")
        file_m.add_command(label="Save As...", command=self.save_rom_as)
        file_m.add_separator()
        file_m.add_command(label="CHR Load...", command=lambda: self._stub("CHR Load"))
        file_m.add_command(label="IPS Patch...", command=lambda: self._stub("IPS Patch"))
        file_m.add_separator()
        file_m.add_command(label="Exit", command=self.root.quit)
        bar.add_cascade(label="File", menu=file_m)

        setting_m = self._menu(bar)
        for label, tab in (
            ("Area...", "Area"),
            ("Map Header...", "Map Header"),
            ("Map...", "Map"),
            ("Bad Guys...", "Bad Guys"),
            ("Game...", "Game"),
        ):
            setting_m.add_command(label=label, command=lambda t=tab: self._goto_tab(t))
        bar.add_cascade(label="Setting", menu=setting_m)

        edit_m = self._menu(bar)
        edit_m.add_command(label="Strings...", command=lambda: self._goto_tab("Text Editor"))
        edit_m.add_command(label="Loop...", command=lambda: self._stub("Loop editor"))
        edit_m.add_command(label="Area Sort...", command=lambda: self._stub("Area Sort"))
        edit_m.add_command(label="Loop Wizard...", command=lambda: self._stub("Loop Wizard"))
        edit_m.add_separator()
        edit_m.add_command(label="Undo", command=lambda: self._stub("Undo"))
        bar.add_cascade(label="Edit", menu=edit_m)

        tool_m = self._menu(bar)
        tool_m.add_command(label="General Setting...", command=lambda: self._stub("General Setting"))
        tool_m.add_command(label="World Data Update...", command=lambda: self._stub("World Data Update"))
        tool_m.add_command(label="Option...", command=self.show_options)
        tool_m.add_command(label="Demo Record...", command=lambda: self._stub("Demo Record"))
        tool_m.add_command(label="Customize Keys...", command=lambda: self._stub("Key Customize"))
        bar.add_cascade(label="Tool", menu=tool_m)

        view_m = self._menu(bar)
        view_m.add_checkbutton(
            label="Toolbar",
            variable=self.show_toolbar,
            command=self._toggle_toolbar,
        )
        view_m.add_checkbutton(
            label="Status Bar",
            variable=self.show_statusbar,
            command=self._toggle_statusbar,
        )
        view_m.add_checkbutton(
            label="Log View",
            variable=self.show_logview,
            command=self._toggle_logview,
        )
        bar.add_cascade(label="View", menu=view_m)

        emu_m = self._menu(bar)
        emu_m.add_command(label="Normal Play", command=lambda: self._emu_action("Normal Play"))
        emu_m.add_command(label="Load Play", command=lambda: self._emu_action("Load Play"))
        emu_m.add_command(label="Page Play", command=lambda: self._emu_action("Page Play"))
        emu_m.add_command(label="Page Play (Half)", command=lambda: self._emu_action("Page Play (Half)"))
        emu_m.add_separator()
        emu_m.add_command(label="Test Play Setting...", command=self.show_test_play_setting)
        emu_m.add_separator()
        emu_m.add_command(label="Save State...", command=lambda: self._stub("Emulator Save State"))
        emu_m.add_command(label="Load State...", command=lambda: self._stub("Emulator Load State"))
        emu_m.add_command(label="Stop", command=lambda: self._emu_action("Stop"))
        bar.add_cascade(label="Emulator", menu=emu_m)

        win_m = self._menu(bar)
        win_m.add_command(label="Next Window", command=self._window_next)
        win_m.add_command(label="Previous Window", command=self._window_prev)
        win_m.add_separator()
        win_m.add_command(label="Close All", command=self._window_close_all)
        win_m.add_command(label="Cascade", command=lambda: self._stub("Cascade MDI windows"))
        bar.add_cascade(label="Window", menu=win_m)

        help_m = self._menu(bar)
        help_m.add_command(label="Version / Readme...", command=self.show_readme)
        help_m.add_command(label="About", command=self.show_about)
        bar.add_cascade(label="Help", menu=help_m)

        self.root.config(menu=bar)
        self.root.bind("<Control-o>", lambda _e: self.open_rom())
        self.root.bind("<Control-s>", lambda _e: self.save_rom())

    def create_toolbar(self) -> None:
        self.toolbar_frame = tk.Frame(self.root, bg=self.accent_blue, height=36)
        self.toolbar_frame.pack(fill="x", padx=0, pady=0)

        buttons = [
            ("Open", self.open_rom),
            ("Save", self.save_rom),
            None,
            ("Area", lambda: self._goto_tab("Area")),
            None,
            ("Bad Guys", lambda: self._set_edit_mode("badguys")),
            ("Map", lambda: self._set_edit_mode("map")),
            None,
            ("Play", lambda: self._emu_action("Normal Play")),
            ("Page", lambda: self._emu_action("Page Play")),
            ("Half", lambda: self._emu_action("Page Play (Half)")),
            ("Stop", lambda: self._emu_action("Stop")),
            ("Test Set", self.show_test_play_setting),
        ]
        for spec in buttons:
            if spec is None:
                tk.Frame(self.toolbar_frame, width=2, bg=self.muted).pack(
                    side="left", fill="y", padx=4, pady=6
                )
                continue
            label, cmd = spec
            tk.Button(
                self.toolbar_frame,
                text=label,
                command=cmd,
                bg=self.field_bg,
                fg=self.text_color,
                activebackground=self.text_color,
                activeforeground=self.bg_color,
                font=("Consolas", 9, "bold"),
                relief="flat",
                padx=8,
                pady=2,
            ).pack(side="left", padx=2, pady=4)

    def create_main_layout(self) -> None:
        body = tk.Frame(self.root, bg=self.bg_color)
        body.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(body)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=(8, 4))

        tabs = [
            ("Map Editor", self._build_map_editor_tab),
            ("Map View", self._build_map_view_tab),
            ("Object List", self._build_object_list_tab),
            ("Object View", self._build_object_view_tab),
            ("Emulator", self._build_emulator_tab),
            ("Area", self._build_area_tab),
            ("Map Header", self._build_map_header_tab),
            ("Map", self._build_map_settings_tab),
            ("Bad Guys", self._build_badguys_tab),
            ("Game", self._build_game_tab),
            ("Text Editor", self._build_text_editor_tab),
            ("ROM Info", self._build_rom_info_tab),
            ("readme", self._build_readme_tab),
        ]
        for idx, (name, builder) in enumerate(tabs):
            frame = tk.Frame(self.notebook, bg=self.bg_color)
            self.notebook.add(frame, text=name)
            self.tab_index[name] = idx
            builder(frame)

        self.log_frame = tk.Frame(body, bg=self.bg_color, height=120)
        self.log_frame.pack(fill="x", padx=8, pady=(0, 4))
        self.log_widget = scrolledtext.ScrolledText(
            self.log_frame,
            height=6,
            bg=self.field_bg,
            fg=self.muted,
            font=("Consolas", 9),
            state="disabled",
            borderwidth=0,
        )
        self.log_widget.pack(fill="both", expand=True)

        self.status_frame = tk.Frame(self.root, bg=self.accent_blue, height=24)
        self.status_frame.pack(fill="x", side="bottom")
        tk.Label(
            self.status_frame,
            textvariable=self.status_var,
            bg=self.accent_blue,
            fg=self.text_color,
            font=("Consolas", 10),
            anchor="w",
        ).pack(fill="x", padx=10, pady=2)

    def _section_label(self, parent: tk.Widget, text: str) -> None:
        tk.Label(
            parent,
            text=text,
            bg=self.bg_color,
            fg=self.text_color,
            font=("Consolas", 11, "bold"),
            anchor="w",
        ).pack(anchor="w", padx=12, pady=(12, 4))

    def _hint(self, parent: tk.Widget, text: str) -> None:
        tk.Label(
            parent,
            text=text,
            bg=self.bg_color,
            fg=self.muted,
            font=("Consolas", 9),
            justify="left",
        ).pack(anchor="w", padx=12, pady=(0, 8))

    def _spin_row(
        self,
        parent: tk.Widget,
        label: str,
        var: tk.IntVar,
        frm: int,
        to: int,
    ) -> None:
        row = tk.Frame(parent, bg=self.bg_color)
        row.pack(fill="x", padx=12, pady=4)
        tk.Label(row, text=label, width=18, anchor="w", bg=self.bg_color, fg=self.text_color,
                 font=("Consolas", 10)).pack(side="left")
        tk.Spinbox(
            row,
            from_=frm,
            to=to,
            textvariable=var,
            width=6,
            bg=self.field_bg,
            fg=self.text_color,
            buttonbackground=self.accent_blue,
            font=("Consolas", 10),
        ).pack(side="left")

    def _build_map_editor_tab(self, tab: tk.Frame) -> None:
        self._section_label(tab, "Map Editor")
        self._hint(tab, "Place terrain tiles and objects (upstream map edit mode). Canvas preview.")
        top = tk.Frame(tab, bg=self.bg_color)
        top.pack(fill="x", padx=12)
        self._spin_row(top, "World", self.world_var, 1, 8)
        self._spin_row(top, "Area", self.area_var, 1, 25)
        self._spin_row(top, "Page", self.page_var, 0, 3)
        self.map_canvas = tk.Canvas(
            tab,
            width=512,
            height=480,
            bg=self.canvas_bg,
            highlightthickness=1,
            highlightbackground=self.accent_blue,
        )
        self.map_canvas.pack(padx=12, pady=8)
        self._draw_grid_canvas(self.map_canvas, "Map Editor — load ROM to edit")

    def _build_map_view_tab(self, tab: tk.Frame) -> None:
        self._section_label(tab, "Map View")
        self._hint(tab, "Scrollable level preview (upstream ghWndMapView).")
        cv = tk.Canvas(
            tab,
            width=512,
            height=480,
            bg=self.canvas_bg,
            highlightthickness=1,
            highlightbackground=self.accent_blue,
        )
        cv.pack(padx=12, pady=8)
        self._draw_grid_canvas(cv, "Map View")

    def _build_object_list_tab(self, tab: tk.Frame) -> None:
        self._section_label(tab, "Object List")
        top = tk.Frame(tab, bg=self.bg_color)
        top.pack(fill="x", padx=12, pady=4)
        tk.Label(top, text="Room ID", bg=self.bg_color, fg=self.text_color,
                 font=("Consolas", 10)).pack(side="left")
        tk.Spinbox(top, from_=0, to=0x7F, textvariable=self.room_id_var, width=5,
                   command=self.refresh_object_list, bg=self.field_bg, fg=self.text_color,
                   font=("Consolas", 10)).pack(side="left", padx=4)
        tk.Button(top, text="Reload", command=self.refresh_object_list,
                  bg=self.accent_blue, fg=self.text_color, font=("Consolas", 9)).pack(side="left", padx=4)
        cols = ("bin", "page", "pos", "type")
        self.obj_tree = ttk.Treeview(tab, columns=cols, show="headings", height=16)
        for c, title in zip(cols, ("Bin", "Page", "Pos", "Type")):
            self.obj_tree.heading(c, text=title)
            self.obj_tree.column(c, width=80 if c != "type" else 240)
        self.obj_tree.pack(fill="both", expand=True, padx=12, pady=8)
        self.obj_tree.bind("<<TreeviewSelect>>", self._on_object_select)
        btn = tk.Frame(tab, bg=self.bg_color)
        btn.pack(fill="x", padx=12, pady=4)
        tk.Button(btn, text="Apply selected bytes", command=self.apply_selected_object,
                  bg=self.accent_blue, fg=self.text_color, font=("Consolas", 9)).pack(side="left", padx=4)

    def _build_object_view_tab(self, tab: tk.Frame) -> None:
        self._section_label(tab, "Object View")
        left = tk.Frame(tab, bg=self.bg_color)
        left.pack(fill="x", padx=12, pady=8)
        for lbl, var in (
            ("Binary (hex)", self.obj_bin_var),
            ("Page", self.obj_page_var),
            ("X", self.obj_x_var),
            ("Y", self.obj_y_var),
        ):
            row = tk.Frame(left, bg=self.bg_color)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=lbl, width=14, anchor="w", bg=self.bg_color, fg=self.text_color,
                     font=("Consolas", 10)).pack(side="left")
            tk.Entry(row, textvariable=var, bg=self.field_bg, fg=self.text_color, width=28,
                     font=("Consolas", 10)).pack(side="left", fill="x", expand=True)
        row = tk.Frame(left, bg=self.bg_color)
        row.pack(fill="x", pady=3)
        tk.Label(row, text="Decoded type", width=14, anchor="w", bg=self.bg_color, fg=self.text_color,
                 font=("Consolas", 10)).pack(side="left")
        tk.Label(row, textvariable=self.obj_type_var, bg=self.bg_color, fg=self.muted,
                 font=("Consolas", 10), wraplength=500, justify="left").pack(side="left", fill="x")
        tk.Button(left, text="Apply bytes to ROM", command=self.apply_selected_object,
                  bg=self.accent_blue, fg=self.text_color, font=("Consolas", 10, "bold")).pack(anchor="w", pady=8)

    def _build_emulator_tab(self, tab: tk.Frame) -> None:
        self._section_label(tab, "Emulator")
        self._hint(tab, "Built-in 6502/NES test play (upstream emuengine + M6502).")
        self.emu_canvas = tk.Canvas(
            tab,
            width=512,
            height=480,
            bg="#000000",
            highlightthickness=1,
            highlightbackground=self.accent_blue,
        )
        self.emu_canvas.pack(padx=12, pady=8)
        self.emu_canvas.create_text(
            256, 240,
            text="NES display\n(emu not wired in Python port)",
            fill=self.muted,
            font=("Consolas", 12),
            justify="center",
        )

    def _build_area_tab(self, tab: tk.Frame) -> None:
        self._section_label(tab, "Area Setting")
        self._spin_row(tab, "Area ID", self.area_var, 1, 25)
        self._hint(tab, "Select world area and page flags (IDM_SETTING_AREA).")

    def _build_map_header_tab(self, tab: tk.Frame) -> None:
        self._section_label(tab, "Map Header")
        self._hint(tab, "2-byte map header at room map address (GetMapHeadData / objlist.c).")
        frm = tk.Frame(tab, bg=self.bg_color)
        frm.pack(anchor="w", padx=12, pady=8)
        for key, values in (
            ("time", MAP_HEAD_TIME),
            ("position", MAP_HEAD_POSITION),
            ("backcolor", MAP_HEAD_BACKCOLOR),
            ("maptype", MAP_HEAD_MAPTYPE),
            ("view", MAP_HEAD_VIEW),
            ("firstblock", MAP_BASIC_BLOCKS),
        ):
            row = tk.Frame(frm, bg=self.bg_color)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=key, width=12, anchor="w", bg=self.bg_color, fg=self.text_color,
                     font=("Consolas", 10)).pack(side="left")
            var = tk.StringVar()
            self.map_head_vars[key] = var
            cb = ttk.Combobox(row, textvariable=var, values=values, state="readonly", width=24)
            cb.pack(side="left")
        tk.Button(tab, text="Apply map header to ROM", command=self.apply_map_header,
                  bg=self.accent_blue, fg=self.text_color, font=("Consolas", 10, "bold")).pack(
            anchor="w", padx=12, pady=8
        )

    def _build_map_settings_tab(self, tab: tk.Frame) -> None:
        self._section_label(tab, "Map Setting")
        row = tk.Frame(tab, bg=self.bg_color)
        row.pack(anchor="w", padx=12, pady=8)
        tk.Label(row, text="Map type", bg=self.bg_color, fg=self.text_color,
                 font=("Consolas", 10)).pack(side="left")
        ttk.Combobox(row, values=MAP_HEAD_MAPTYPE, state="readonly", width=14).pack(side="left", padx=8)
        self._hint(tab, "Background, view, first block, map attribute (IDM_SETTING_MAP).")

    def _build_badguys_tab(self, tab: tk.Frame) -> None:
        self._section_label(tab, "Bad Guys")
        self._hint(tab, "Enemy placement mode — toolbar Map / Bad Guys toggles edit mode.")
        lb = tk.Listbox(tab, bg=self.field_bg, fg=self.text_color, font=("Consolas", 10), height=14)
        lb.pack(fill="both", expand=True, padx=12, pady=8)
        for i, name in enumerate(BADGUYS_NAMES[:32]):
            if name != "Empty":
                lb.insert("end", f"{i:02X} — {name}")

    def _build_game_tab(self, tab: tk.Frame) -> None:
        self._section_label(tab, "Game Setting")
        self._hint(tab, "Warp zones, coins for 1-up, Koopa, difficulty (IDM_SETTING_GAME).")
        for lbl in ("Coins for 1-up", "Warp A", "Warp B", "Clear world", "Difficulty"):
            row = tk.Frame(tab, bg=self.bg_color)
            row.pack(fill="x", padx=12, pady=4)
            tk.Label(row, text=lbl, width=16, anchor="w", bg=self.bg_color, fg=self.text_color,
                     font=("Consolas", 10)).pack(side="left")
            tk.Spinbox(row, from_=0, to=99, width=6, bg=self.field_bg, fg=self.text_color,
                       font=("Consolas", 10)).pack(side="left")

    def _build_text_editor_tab(self, tab: tk.Frame) -> None:
        self._section_label(tab, "Edit Strings")
        self._hint(tab, "HUD strings + upstream string table slots (IDM_EDIT_STRINGS).")
        self.text_entries.clear()
        for label, prg_offset in TEXT_OFFSETS_PRG.items():
            row = tk.Frame(tab, bg=self.bg_color)
            row.pack(fill="x", padx=12, pady=6)
            off = self._file_offset(prg_offset)
            tk.Label(
                row,
                text=f"{label}  PRG {prg_offset:#06x}  file {off:#06x}",
                bg=self.bg_color,
                fg=self.text_color,
                width=40,
                anchor="w",
                font=("Consolas", 10),
            ).pack(side="left")
            entry = tk.Entry(
                row,
                bg=self.field_bg,
                fg=self.text_color,
                insertbackground=self.text_color,
                font=("Consolas", 12),
                state="disabled",
            )
            entry.pack(side="left", fill="x", expand=True)
            self.text_entries[label] = entry
        extra = tk.LabelFrame(
            tab,
            text="Other strings (upstream STRING_STRINGDATA_01–20)",
            bg=self.bg_color,
            fg=self.text_color,
            font=("Consolas", 10, "bold"),
        )
        extra.pack(fill="x", padx=12, pady=8)
        for name in SMB_STRING_NAMES[:6]:
            row = tk.Frame(extra, bg=self.bg_color)
            row.pack(fill="x", padx=8, pady=2)
            tk.Label(row, text=name, width=14, anchor="w", bg=self.bg_color, fg=self.muted,
                     font=("Consolas", 9)).pack(side="left")
            tk.Entry(row, bg=self.field_bg, fg=self.text_color, state="disabled",
                     font=("Consolas", 10)).pack(side="left", fill="x", expand=True)
        btn = tk.Frame(tab, bg=self.bg_color)
        btn.pack(fill="x", padx=12, pady=8)
        tk.Button(
            btn,
            text="Apply HUD text to ROM",
            command=self.apply_text_fields,
            bg=self.accent_blue,
            fg=self.text_color,
            font=("Consolas", 10, "bold"),
            activebackground=self.text_color,
            activeforeground=self.bg_color,
        ).pack(side="left")

    def _build_rom_info_tab(self, tab: tk.Frame) -> None:
        self._section_label(tab, "ROM / File")
        self.rom_status_label = tk.Label(
            tab,
            text="No ROM loaded.",
            bg=self.bg_color,
            fg=self.text_color,
            font=("Consolas", 12),
            justify="left",
        )
        self.rom_status_label.pack(anchor="w", padx=12, pady=8)
        self._hint(
            tab,
            "iNES .nes only. PRG/CHR from header. Do not redistribute copyrighted ROMs.",
        )

    def _build_readme_tab(self, tab: tk.Frame) -> None:
        txt = scrolledtext.ScrolledText(
            tab,
            wrap="word",
            bg=self.field_bg,
            fg=self.text_color,
            font=("Consolas", 10),
            borderwidth=0,
        )
        txt.pack(fill="both", expand=True, padx=8, pady=8)
        txt.insert("1.0", f"{README_EN_US}\n{PYTHON_PORT_NOTE}\n{UPSTREAM_README_URL}\n")
        txt.config(state="disabled")

    def _draw_grid_canvas(self, canvas: tk.Canvas, title: str) -> None:
        canvas.delete("all")
        w, h = int(canvas["width"]), int(canvas["height"])
        canvas.create_text(w // 2, 20, text=title, fill=self.text_color, font=("Consolas", 11, "bold"))
        for x in range(0, w, 16):
            canvas.create_line(x, 40, x, h, fill="#1a2a3a")
        for y in range(40, h, 16):
            canvas.create_line(0, y, w, y, fill="#1a2a3a")

    def _log(self, msg: str) -> None:
        if self.log_widget is None:
            return
        self.log_widget.config(state="normal")
        self.log_widget.insert("end", msg + "\n")
        self.log_widget.see("end")
        self.log_widget.config(state="disabled")

    def _set_status(self, text: str) -> None:
        self.status_var.set(text)

    def _refresh_title(self) -> None:
        title = self.APP_TITLE
        if self.rom_path:
            title += f" — {os.path.basename(self.rom_path)}"
        if self.data_changed:
            title += "*"
        self.root.title(title)

    def _set_changed(self, changed: bool) -> None:
        self.data_changed = changed
        self._refresh_title()

    def _current_room_id(self) -> int:
        if self.rom_core is None:
            return 0
        rid = self.rom_core.room_id_for_area(self.area_var.get() - 1)
        try:
            manual = int(self.room_id_var.get())
            if manual > 0:
                return manual & 0x7F
        except tk.TclError:
            pass
        return rid

    def refresh_object_list(self) -> None:
        if not self.obj_tree or self.rom_core is None:
            return
        for item in self.obj_tree.get_children():
            self.obj_tree.delete(item)
        room_id = self._current_room_id()
        self.room_id_var.set(room_id)
        if self.edit_mode == "badguys":
            self.parsed_objects = self.rom_core.iter_badguys(room_id)
        else:
            self.parsed_objects = self.rom_core.iter_map(room_id)
        for obj in self.parsed_objects:
            bin_s = " ".join(f"{b:02x}" for b in obj.raw)
            self.obj_tree.insert(
                "",
                "end",
                iid=str(obj.index),
                values=(bin_s, str(obj.page), f"({obj.x},{obj.y})", obj.label),
            )
        if self.parsed_objects:
            self.obj_tree.selection_set("0")
            self._show_object(0)
        self._log(f"Loaded {len(self.parsed_objects)} {'bad guy' if self.edit_mode == 'badguys' else 'map'} objects @ room {room_id:02X}")

    def _on_object_select(self, _event: tk.Event | None = None) -> None:
        if not self.obj_tree:
            return
        sel = self.obj_tree.selection()
        if not sel:
            return
        self._show_object(int(sel[0]))

    def _show_object(self, index: int) -> None:
        if index < 0 or index >= len(self.parsed_objects):
            return
        self.selected_obj_index = index
        obj = self.parsed_objects[index]
        self.obj_bin_var.set(" ".join(f"{b:02x}" for b in obj.raw))
        self.obj_page_var.set(str(obj.page))
        self.obj_x_var.set(str(obj.x))
        self.obj_y_var.set(str(obj.y))
        self.obj_type_var.set(obj.label)

    def apply_selected_object(self) -> None:
        if self.rom_core is None or not self.parsed_objects:
            messagebox.showwarning(PROGRAM_NAME, "No object selected.")
            return
        idx = self.selected_obj_index
        if idx < 0 or idx >= len(self.parsed_objects):
            return
        text = self.obj_bin_var.get().strip()
        try:
            parts = text.split()
            data = bytes(int(p, 16) for p in parts)
        except ValueError:
            messagebox.showerror(PROGRAM_NAME, "Invalid hex bytes (e.g. 'a5 01').")
            return
        obj = self.parsed_objects[idx]
        if len(data) != len(obj.raw):
            messagebox.showerror(PROGRAM_NAME, f"Expected {len(obj.raw)} byte(s) for this opcode.")
            return
        self.rom_core.write_object_bytes(obj.prg_offset, data)
        self._set_changed(True)
        self.refresh_object_list()
        self.obj_tree.selection_set(str(idx))
        self._show_object(idx)
        self._log(f"Patched object {idx} @ PRG {obj.prg_offset:#06x}: {text}")

    def load_map_header_ui(self) -> None:
        if self.rom_core is None or not self.map_head_vars:
            return
        hdr = self.rom_core.get_map_header(self._current_room_id())
        if len(hdr) < 2:
            return
        self.map_head_vars["time"].set(MAP_HEAD_TIME[(hdr[0] >> 6) & 3])
        self.map_head_vars["position"].set(MAP_HEAD_POSITION[(hdr[0] >> 3) & 7])
        self.map_head_vars["backcolor"].set(MAP_HEAD_BACKCOLOR[hdr[0] & 7])
        self.map_head_vars["maptype"].set(MAP_HEAD_MAPTYPE[(hdr[1] >> 6) & 3])
        self.map_head_vars["view"].set(MAP_HEAD_VIEW[(hdr[1] >> 4) & 3])
        bb = hdr[1] & 0x0F
        self.map_head_vars["firstblock"].set(
            MAP_BASIC_BLOCKS[bb] if bb < len(MAP_BASIC_BLOCKS) else MAP_BASIC_BLOCKS[0]
        )

    def apply_map_header(self) -> None:
        if self.rom_core is None:
            messagebox.showwarning(PROGRAM_NAME, "Open a ROM first.")
            return
        try:
            t = MAP_HEAD_TIME.index(self.map_head_vars["time"].get())
            p = MAP_HEAD_POSITION.index(self.map_head_vars["position"].get())
            b = MAP_HEAD_BACKCOLOR.index(self.map_head_vars["backcolor"].get())
            mt = MAP_HEAD_MAPTYPE.index(self.map_head_vars["maptype"].get())
            v = MAP_HEAD_VIEW.index(self.map_head_vars["view"].get())
            fb = MAP_BASIC_BLOCKS.index(self.map_head_vars["firstblock"].get())
        except ValueError as e:
            messagebox.showerror(PROGRAM_NAME, f"Invalid header field: {e}")
            return
        hdr = bytes([((t & 3) << 6) | ((p & 7) << 3) | (b & 7), ((mt & 3) << 6) | ((v & 3) << 4) | (fb & 0x0F)])
        self.rom_core.set_map_header(self._current_room_id(), hdr)
        self._set_changed(True)
        self._log(f"Map header applied: {hdr[0]:02x} {hdr[1]:02x}")

    def _refresh_ui_state(self) -> None:
        loaded = self.rom_data is not None
        room = self._current_room_id() if loaded else 0
        self._set_status(
            f"ROM: {'loaded' if loaded else 'none'}  |  Mode: {self.edit_mode}  |  "
            f"W{self.world_var.get()} A{self.area_var.get()} room {room:02X} objs {len(self.parsed_objects)}"
        )
        if loaded:
            self.refresh_object_list()
            self.load_map_header_ui()
        if self.map_canvas and loaded:
            self._draw_grid_canvas(self.map_canvas, f"Map Editor — room {room:02X}")

    def _goto_tab(self, name: str) -> None:
        if self.notebook is None or name not in self.tab_index:
            return
        self.notebook.select(self.tab_index[name])
        self._log(f"View: {name}")

    def _set_edit_mode(self, mode: str) -> None:
        self.edit_mode = mode
        tab = "Bad Guys" if mode == "badguys" else "Map Editor"
        self._goto_tab(tab)
        if self.rom_core:
            self.refresh_object_list()
        self._refresh_ui_state()
        self._log(f"Edit mode: {mode}")

    def _toggle_toolbar(self) -> None:
        if not self.toolbar_frame:
            return
        if self.show_toolbar.get():
            self.toolbar_frame.pack(fill="x")
        else:
            self.toolbar_frame.pack_forget()

    def _toggle_statusbar(self) -> None:
        if self.status_frame:
            if self.show_statusbar.get():
                self.status_frame.pack(fill="x", side="bottom")
            else:
                self.status_frame.pack_forget()

    def _toggle_logview(self) -> None:
        if self.log_frame:
            if self.show_logview.get():
                self.log_frame.pack(fill="x", padx=8, pady=(0, 4))
            else:
                self.log_frame.pack_forget()

    def _stub(self, feature: str) -> None:
        if not self.rom_data and feature not in ("Key Customize", "General Setting", "Option"):
            messagebox.showwarning(PROGRAM_NAME, "Open a ROM first.")
            return
        messagebox.showinfo(
            PROGRAM_NAME,
            f"{feature}\n\nNot implemented in the Python port.\n"
            "Full logic lives in the upstream C sources (Maseya/SMB-Utility).",
        )
        self._log(f"Stub: {feature}")

    def _emu_action(self, action: str) -> None:
        if not self.rom_data:
            messagebox.showwarning(PROGRAM_NAME, "Open a ROM before test play.")
            return
        self._goto_tab("Emulator")
        self._log(f"Emulator: {action}")
        self._set_status(f"Emulator: {action} (stub)")
        if action == "Stop":
            messagebox.showinfo(PROGRAM_NAME, "Emulator stopped.")

    def _window_next(self) -> None:
        if self.notebook:
            i = self.notebook.index(self.notebook.select())
            n = self.notebook.index("end")
            self.notebook.select((i + 1) % n)

    def _window_prev(self) -> None:
        if self.notebook:
            i = self.notebook.index(self.notebook.select())
            n = self.notebook.index("end")
            self.notebook.select((i - 1) % n)

    def _window_close_all(self) -> None:
        self._goto_tab("Map Editor")

    def show_readme(self) -> None:
        self._show_text_dialog("SMB Utility readme (en-US, 1.08)", README_EN_US)

    def show_about(self) -> None:
        body = f"{PROGRAM_NAME} {APP_VERSION}\n\n{README_EN_US}\n{PYTHON_PORT_NOTE}\n{UPSTREAM_README_URL}\n"
        self._show_text_dialog("About", body)

    def show_options(self) -> None:
        win = tk.Toplevel(self.root)
        win.title("Option")
        win.configure(bg=self.bg_color)
        win.geometry("400x180")
        win.transient(self.root)
        tk.Checkbutton(
            win,
            text="Show message on save",
            variable=self.msg_on_save,
            bg=self.bg_color,
            fg=self.text_color,
            selectcolor=self.field_bg,
            activebackground=self.bg_color,
            font=("Consolas", 10),
        ).pack(anchor="w", padx=20, pady=20)
        tk.Button(
            win,
            text="OK",
            command=win.destroy,
            bg=self.accent_blue,
            fg=self.text_color,
            font=("Consolas", 10, "bold"),
        ).pack(pady=10)

    def show_test_play_setting(self) -> None:
        win = tk.Toplevel(self.root)
        win.title("Test Play Setting")
        win.configure(bg=self.bg_color)
        win.geometry("420x280")
        win.transient(self.root)
        for lbl, values in (
            ("Mario state", ("Small Mario", "Super Mario", "Fire Mario")),
            ("Start position", ("Current page", "From destination page", "Mario start")),
        ):
            row = tk.Frame(win, bg=self.bg_color)
            row.pack(fill="x", padx=16, pady=8)
            tk.Label(row, text=lbl, width=14, anchor="w", bg=self.bg_color, fg=self.text_color,
                     font=("Consolas", 10)).pack(side="left")
            ttk.Combobox(row, values=values, state="readonly", width=22).pack(side="left")
        tk.Checkbutton(
            win,
            text="Invincible",
            bg=self.bg_color,
            fg=self.text_color,
            selectcolor=self.field_bg,
            font=("Consolas", 10),
        ).pack(anchor="w", padx=16, pady=8)
        tk.Button(win, text="OK", command=win.destroy, bg=self.accent_blue, fg=self.text_color,
                  font=("Consolas", 10, "bold")).pack(pady=12)

    def _show_text_dialog(self, title: str, body: str) -> None:
        win = tk.Toplevel(self.root)
        win.title(title)
        win.configure(bg=self.bg_color)
        win.geometry("720x520")
        win.transient(self.root)
        text = scrolledtext.ScrolledText(
            win,
            wrap="word",
            bg=self.field_bg,
            fg=self.text_color,
            font=("Consolas", 10),
            borderwidth=0,
        )
        text.pack(fill="both", expand=True, padx=10, pady=10)
        text.insert("1.0", body)
        text.config(state="disabled")
        tk.Button(
            win,
            text="Close",
            command=win.destroy,
            bg=self.accent_blue,
            fg=self.text_color,
            font=("Consolas", 10, "bold"),
        ).pack(pady=(0, 10))

    def _has_ines(self) -> bool:
        return (
            self.rom_data is not None
            and len(self.rom_data) >= INES_HEADER_SIZE
            and bytes(self.rom_data[:4]) == INES_MAGIC
        )

    def _file_offset(self, prg_offset: int) -> int:
        return prg_to_file_offset(prg_offset, self._has_ines())

    def _validate_rom(self) -> str | None:
        if self.rom_data is None:
            return "No ROM data."
        if len(self.rom_data) < 8192:
            return "File too small for SMB1."
        if not self._has_ines():
            return "No iNES header (expected NES\\x1a)."
        if self.rom_data[4] < 2:
            return f"Unexpected PRG size ({self.rom_data[4]} x 16KB)."
        max_off = max(
            self._file_offset(off) + TEXT_LENGTHS[label]
            for label, off in TEXT_OFFSETS_PRG.items()
        )
        if len(self.rom_data) < max_off:
            return f"ROM too short (need {max_off:#x} bytes)."
        return None

    def _update_rom_info(self) -> None:
        if self.rom_status_label is None:
            return
        if self.rom_data is None:
            self.rom_status_label.config(text="No ROM loaded.")
            return
        err = self._validate_rom()
        lines = [f"Loaded: {self.rom_path}", f"Size: {len(self.rom_data):,} bytes"]
        if self._has_ines():
            lines.append(
                f"iNES: PRG {self.rom_data[4]}x16KB, CHR {self.rom_data[5]}x8KB, "
                f"mapper {self.rom_data[6] & 0x0F}"
            )
        lines.append(f"Warning: {err}" if err else "US SMB1 HUD offsets OK.")
        self.rom_status_label.config(text="\n".join(lines))

    def _set_entries_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        for entry in self.text_entries.values():
            entry.config(state=state)

    def open_rom(self) -> None:
        path = filedialog.askopenfilename(
            title="Open iNES ROM",
            filetypes=[("NES ROM (*.nes)", "*.nes"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "rb") as f:
                data = f.read()
            if not data:
                messagebox.showerror(PROGRAM_NAME, "File is empty.")
                return
            self.rom_data = bytearray(data)
            self.rom_path = path
            self.rom_core = SMBRomEngine(self.rom_data)
            self.room_id_var.set(self.rom_core.room_id_for_area(self.area_var.get() - 1))
            self._set_changed(False)
            err = self._validate_rom()
            if err and "too short" in err:
                messagebox.showerror(PROGRAM_NAME, err)
                self.rom_data = None
                self.rom_path = ""
                self.rom_core = None
                self.parsed_objects = []
                self._set_entries_enabled(False)
            else:
                if err:
                    messagebox.showwarning(PROGRAM_NAME, err)
                self.load_text_fields()
                self._set_entries_enabled(True)
            self._update_rom_info()
            self._refresh_ui_state()
            self._refresh_title()
            self._log(f"Opened: {path}")
        except OSError as e:
            messagebox.showerror(PROGRAM_NAME, str(e))

    def save_rom(self) -> None:
        if self.rom_data is None:
            messagebox.showwarning(PROGRAM_NAME, "Open a ROM first.")
            return
        if self.rom_path:
            self._save_to_path(self.rom_path)
        else:
            self.save_rom_as()

    def save_rom_as(self) -> None:
        if self.rom_data is None:
            return
        path = filedialog.asksaveasfilename(
            title="Save iNES ROM",
            initialfile=os.path.basename(self.rom_path) if self.rom_path else "smb1_edit.nes",
            defaultextension=".nes",
            filetypes=[("NES ROM (*.nes)", "*.nes"), ("All files", "*.*")],
        )
        if path:
            self._save_to_path(path)

    def _save_to_path(self, path: str) -> None:
        err = self._validate_rom()
        if err and "too short" in err:
            messagebox.showerror(PROGRAM_NAME, err)
            return
        self.apply_text_fields(silent=True)
        if self.rom_core:
            self.rom_core.save_tables()
        try:
            with open(path, "wb") as f:
                f.write(self.rom_data)
            self.rom_path = path
            self._set_changed(False)
            self._update_rom_info()
            self._refresh_title()
            self._log(f"Saved: {path}")
            if self.msg_on_save.get():
                messagebox.showinfo(PROGRAM_NAME, f"ROM saved:\n{path}")
        except OSError as e:
            messagebox.showerror(PROGRAM_NAME, str(e))

    def load_text_fields(self) -> None:
        if self.rom_data is None:
            return
        for label, prg_offset in TEXT_OFFSETS_PRG.items():
            start = self._file_offset(prg_offset)
            raw = bytes(self.rom_data[start : start + TEXT_LENGTHS[label]])
            entry = self.text_entries[label]
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, smb_decode(raw))

    def apply_text_fields(self, silent: bool = False) -> None:
        if self.rom_data is None:
            messagebox.showwarning(PROGRAM_NAME, "Open a ROM first.")
            return
        err = self._validate_rom()
        if err and "too short" in err:
            messagebox.showerror(PROGRAM_NAME, err)
            return
        for label, prg_offset in TEXT_OFFSETS_PRG.items():
            start = self._file_offset(prg_offset)
            enc = smb_encode(self.text_entries[label].get(), TEXT_LENGTHS[label])
            for i, b in enumerate(enc):
                self.rom_data[start + i] = b
        self._set_changed(True)
        if not silent:
            messagebox.showinfo(PROGRAM_NAME, "HUD text applied in memory. Use File → Save.")
        self._log("Applied HUD text patches.")


if __name__ == "__main__":
    root = tk.Tk()
    SMBUtility(root)
    root.mainloop()
