"""
SECRET CIPHER — Tkinter GUI Application
Run: python3 cipher_app.py
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import math
import re

# ── CIPHER ENGINE ─────────────────────────────────────────────

NUM_TO_SYM = {
    0:"[0]", 1:"@", 2:"#", 3:"$", 4:"!!!",
    5:"&", 6:"$$", 7:"(", 8:")", 9:"!!", 10:"~"
}
SYM_TO_NUM = {v: k for k, v in NUM_TO_SYM.items()}

def encode_number(n):
    if n == 0:
        return "[0]"
    sq = math.isqrt(n)
    if sq * sq == n:
        for a in range(min(sq, 10) + 1):
            b = sq - a
            if 0 <= b <= 10:
                return f"({NUM_TO_SYM[a]}+{NUM_TO_SYM[b]})^2"
    cb = round(n ** (1/3))
    for c in [cb-1, cb, cb+1]:
        if c >= 0 and c**3 == n:
            for a in range(min(c, 10) + 1):
                b = c - a
                if 0 <= b <= 10:
                    return f"({NUM_TO_SYM[a]}+{NUM_TO_SYM[b]})^3"
    parts, rem = [], n
    while rem > 0:
        chunk = min(rem, 10)
        parts.append(NUM_TO_SYM[chunk])
        rem -= chunk
    return "(" + "+".join(parts) + ")"

def encode(text):
    words = text.upper().split(" ")
    encoded_words = []
    for word in words:
        letter_tokens = []
        for ch in word:
            if ch.isalpha():
                letter_tokens.append(encode_number(ord(ch) - 65))
            else:
                letter_tokens.append(ch)
        encoded_words.append("  ".join(letter_tokens))
    return " / ".join(encoded_words)

def parse_sym(s):
    return SYM_TO_NUM.get(s.strip(), None)

def decode_token(token):
    token = token.strip()
    if token == "[0]":
        return "A"
    if "^" in token:
        paren_end = token.rfind(")")
        inner = token[1:paren_end]
        power_str = token[paren_end+2:]
        power = int(power_str) if power_str.isdigit() else 1
    elif token.startswith("(") and token.endswith(")"):
        inner = token[1:-1]
        power = 1
    else:
        return token
    parts = re.split(r'(\+|-)', inner)
    total, op = 0, "+"
    for p in parts:
        p = p.strip()
        if p in ("+", "-"):
            op = p
        else:
            val = parse_sym(p)
            if val is None:
                return token
            total += val if op == "+" else -val
    result = total ** power
    if 0 <= result <= 25:
        return chr(result + 65)
    return token

def decode(text):
    words = text.split(" / ")
    decoded_words = []
    for word in words:
        letter_tokens = word.split("  ")
        decoded_words.append("".join(decode_token(t) for t in letter_tokens))
    return " ".join(decoded_words)

def get_steps(text):
    lines = []
    for ch in text.upper():
        if ch == " ":
            lines.append("  [space]  →  word separator")
        elif ch.isalpha():
            n = ord(ch) - 65
            sym = encode_number(n)
            lines.append(f"  {ch}  →  num {n:2d}  →  {sym}")
        else:
            lines.append(f"  '{ch}'  →  kept as-is")
    return "\n".join(lines)


# ── THEME ─────────────────────────────────────────────────────

BG       = "#1A1A2E"
BG2      = "#16213E"
BG3      = "#0F3460"
ACCENT   = "#E94560"
GOLD     = "#C9A84C"
FG       = "#E8ECF6"
FG2      = "#A0AEC0"
MONO     = "#7FDBCA"
SUCCESS  = "#68D391"
ENTRY_BG = "#0D1B2A"

F_TITLE = ("Segoe UI", 20, "bold")
F_HEAD  = ("Segoe UI", 11, "bold")
F_BODY  = ("Segoe UI", 10)
F_MONO  = ("Courier New", 10)
F_SMALL = ("Segoe UI", 9)


# ── APP ───────────────────────────────────────────────────────

class CipherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Secret Cipher")
        self.geometry("860x660")
        self.minsize(720, 560)
        self.configure(bg=BG)
        self._build()

    def _build(self):
        # Title bar
        bar = tk.Frame(self, bg=BG2, pady=14)
        bar.pack(fill="x")
        tk.Label(bar, text="SECRET CIPHER", font=F_TITLE,
                 bg=BG2, fg=ACCENT).pack(side="left", padx=24)
        tk.Label(bar, text="3-Layer Encryption System", font=F_BODY,
                 bg=BG2, fg=FG2).pack(side="left", padx=6)

        # Tab buttons
        tabs = tk.Frame(self, bg=BG3)
        tabs.pack(fill="x")
        self._tab_btns = {}
        for label, key in [("  Encode  ", "encode"), ("  Decode  ", "decode")]:
            b = tk.Button(tabs, text=label, font=F_HEAD,
                          bg=ACCENT, fg=FG, bd=0, padx=18, pady=9,
                          cursor="hand2", relief="flat",
                          command=lambda k=key: self._switch(k))
            b.pack(side="left")
            self._tab_btns[key] = b

        # Content area
        self.body = tk.Frame(self, bg=BG)
        self.body.pack(fill="both", expand=True, padx=28, pady=20)

        self._build_encode()
        self._build_decode()
        self._switch("encode")

    # ── TAB SWITCH ────────────────────────────────────────────

    def _switch(self, key):
        self.active = key
        for k, b in self._tab_btns.items():
            b.config(bg=ACCENT if k == key else BG3)
        for k in ("encode", "decode"):
            f = getattr(self, f"_f_{k}")
            if k == key:
                f.pack(fill="both", expand=True)
            else:
                f.pack_forget()

    # ── ENCODE TAB ────────────────────────────────────────────

    def _build_encode(self):
        f = tk.Frame(self.body, bg=BG)
        self._f_encode = f

        tk.Label(f, text="Enter text to encode", font=F_HEAD,
                 bg=BG, fg=FG2).pack(anchor="w", pady=(0, 4))

        self.enc_in = tk.Text(f, height=4, font=F_MONO, bg=ENTRY_BG,
                               fg=FG, insertbackground=ACCENT,
                               relief="flat", bd=8, wrap="word")
        self.enc_in.pack(fill="x")

        # Buttons row
        row = tk.Frame(f, bg=BG, pady=10)
        row.pack(fill="x")
        self._btn(row, "Encode →", self._do_encode, primary=True).pack(side="left", padx=(0, 8))
        self._btn(row, "Clear", self._clear_enc).pack(side="left")
        self._btn(row, "Copy", self._copy_enc).pack(side="right")

        tk.Label(f, text="Encrypted output", font=F_HEAD,
                 bg=BG, fg=FG2).pack(anchor="w", pady=(8, 4))

        self.enc_out = tk.Text(f, height=4, font=F_MONO, bg=ENTRY_BG,
                                fg=MONO, insertbackground=ACCENT,
                                relief="flat", bd=8, wrap="word", state="disabled")
        self.enc_out.pack(fill="x")

        # Steps checkbox
        srow = tk.Frame(f, bg=BG, pady=6)
        srow.pack(fill="x")
        self._show_steps = tk.BooleanVar(value=False)
        tk.Checkbutton(srow, text="Show step-by-step breakdown",
                       variable=self._show_steps, font=F_SMALL,
                       bg=BG, fg=FG2, selectcolor=BG3,
                       activebackground=BG, activeforeground=FG,
                       command=self._toggle_steps).pack(side="left")

        # Steps area (hidden by default)
        self._steps_frame = tk.Frame(f, bg=BG)
        tk.Label(self._steps_frame, text="Breakdown", font=F_HEAD,
                 bg=BG, fg=FG2).pack(anchor="w", pady=(4, 4))
        self._steps_box = scrolledtext.ScrolledText(
            self._steps_frame, height=9, font=F_MONO,
            bg=ENTRY_BG, fg=GOLD, relief="flat", bd=8, state="disabled")
        self._steps_box.pack(fill="both", expand=True)

    def _do_encode(self):
        text = self.enc_in.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("Empty", "Please enter some text.")
            return
        self._set(self.enc_out, encode(text))
        if self._show_steps.get():
            self._set(self._steps_box, get_steps(text))

    def _toggle_steps(self):
        if self._show_steps.get():
            self._steps_frame.pack(fill="both", expand=True)
            text = self.enc_in.get("1.0", "end").strip()
            if text:
                self._set(self._steps_box, get_steps(text))
        else:
            self._steps_frame.pack_forget()

    def _clear_enc(self):
        self.enc_in.delete("1.0", "end")
        self._set(self.enc_out, "")
        self._set(self._steps_box, "")

    def _copy_enc(self):
        t = self.enc_out.get("1.0", "end").strip()
        if t:
            self.clipboard_clear()
            self.clipboard_append(t)
            messagebox.showinfo("Copied!", "Encrypted text copied to clipboard.")

    # ── DECODE TAB ────────────────────────────────────────────

    def _build_decode(self):
        f = tk.Frame(self.body, bg=BG)
        self._f_decode = f

        tk.Label(f, text="Paste cipher text to decode", font=F_HEAD,
                 bg=BG, fg=FG2).pack(anchor="w", pady=(0, 4))

        self.dec_in = tk.Text(f, height=4, font=F_MONO, bg=ENTRY_BG,
                               fg=MONO, insertbackground=ACCENT,
                               relief="flat", bd=8, wrap="word")
        self.dec_in.pack(fill="x")

        row = tk.Frame(f, bg=BG, pady=10)
        row.pack(fill="x")
        self._btn(row, "Decode →", self._do_decode, primary=True).pack(side="left", padx=(0, 8))
        self._btn(row, "Clear", self._clear_dec).pack(side="left")
        self._btn(row, "Copy", self._copy_dec).pack(side="right")

        tk.Label(f, text="Decoded output", font=F_HEAD,
                 bg=BG, fg=FG2).pack(anchor="w", pady=(8, 4))

        self.dec_out = tk.Text(f, height=4, font=F_MONO, bg=ENTRY_BG,
                                fg=SUCCESS, insertbackground=ACCENT,
                                relief="flat", bd=8, wrap="word", state="disabled")
        self.dec_out.pack(fill="x")

        # Format hint box
        hint = tk.Frame(f, bg=BG3, pady=10, padx=16)
        hint.pack(fill="x", pady=(20, 0))
        tk.Label(hint, text="Format guide", font=F_HEAD,
                 bg=BG3, fg=GOLD).pack(anchor="w")
        for line in [
            "  single space   →  parts of one letter    ( ~ # )",
            "  double space   →  between letters         ( H  E  L )",
            "  ' / '          →  between words",
        ]:
            tk.Label(hint, text=line, font=F_MONO,
                     bg=BG3, fg=FG2).pack(anchor="w")

    def _do_decode(self):
        text = self.dec_in.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("Empty", "Please paste cipher text.")
            return
        try:
            self._set(self.dec_out, decode(text))
        except Exception as e:
            messagebox.showerror("Error", f"Could not decode:\n{e}")

    def _clear_dec(self):
        self.dec_in.delete("1.0", "end")
        self._set(self.dec_out, "")

    def _copy_dec(self):
        t = self.dec_out.get("1.0", "end").strip()
        if t:
            self.clipboard_clear()
            self.clipboard_append(t)
            messagebox.showinfo("Copied!", "Decoded text copied to clipboard.")

    # ── HELPERS ───────────────────────────────────────────────

    def _btn(self, parent, text, cmd, primary=False):
        return tk.Button(parent, text=text, command=cmd, font=F_BODY,
                         cursor="hand2", relief="flat", bd=0,
                         bg=ACCENT if primary else BG3, fg=FG,
                         padx=16, pady=6,
                         activebackground="#c73652", activeforeground=FG)

    def _set(self, widget, text):
        widget.config(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.config(state="disabled")


if __name__ == "__main__":
    CipherApp().mainloop()