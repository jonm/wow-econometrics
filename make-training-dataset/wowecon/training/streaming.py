# Copyright (C) 2017, 2018 Jonathan Moore
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import cStringIO

class StreamingSourceIterator:
    """Files support the iterator protocol. Each iteration returns the
same result as file.readline(), and iteration ends when the readline()
method returns an empty string."""
    def __init__(self, ss):
        self._ss = ss

    def __iter__(self):
        return self

    def next(self):
        s = self._ss.readline()
        if len(s) == 0: raise StopIteration()
        return s

class StreamingSource:
    """Creates a file-like object from a generator that produces strings.
See https://docs.python.org/2.4/lib/bltin-file-objects.html"""
    
    def __init__(self, gen):
        self._gen = gen
        self._extra = ''
        self._pos = 0
        self.closed = False

    def close(self):
        self.closed = True

    def flush(self): pass
    
    # fileno() not provided
    # isatty() not provided

    def next(self):
        if self.closed:
            raise ValueError("cannot read from closed file-like object")
        if len(self._extra) > 0:
            out = self._extra
            self._pos += len(self._extra)
            self._extra = ''
            return out
        out = self._gen.next()
        while len(out) == 0: out = self._gen.next()
        self._pos += len(out)
        return out

    def read(self, size=None):
        if self.closed:
            raise ValueError("cannot read from closed file-like object")

        if size is None or size < 0:
            # read to EOF
            buf = cStringIO.StringIO()
            while True:
                try:
                    buf.write(self.next())
                except StopIteration:
                    break
            return buf.getvalue()

        if len(self._extra) > 0 and len(self._extra) >= size:
            out = self._extra[:size]
            self._extra = self._extra[size:]
            self._pos += size
            return out

        buf = cStringIO.StringIO()
        written = 0
        while written < size:
            try:
                s = self.next()
                if len(s) <= (size - written):
                    buf.write(s)
                    written += len(s)
                else:
                    buf.write(s[:(size - written)])
                    self._extra = s[(size - written):]
                    self._pos -= len(self._extra)
                    written += size - written
            except StopIteration:
                break
        return buf.getvalue()
        
    def readline(self, size=None):
        if self.closed:
            raise ValueError("cannot read from closed file-like object")

        if size is None or size < 0:
            # read to EOF or newline
            buf = cStringIO.StringIO()
            while True:
                try:
                    s = self.next()
                    idx = s.find('\n')
                    if idx > 0:
                        buf.write(s[:idx+1])
                        self._extra = s[idx+1:]
                        self._pos -= len(self._extra)
                        break
                    else:
                        buf.write(s)
                except StopIteration:
                    break
            return buf.getvalue()

        if len(self._extra) > 0:
            idx = self._extra.find('\n')
            if idx > 0:
                out = self._extra[:idx+1] # include newline
                self._extra = self._extra[idx+1:]
                self._pos += len(out)
                return out

        buf = cStringIO.StringIO()
        written = 0
        while written < size:
            try:
                s = self.next()
                idx = s.find('\n')
                if idx > 0 and (written + idx + 1 < size):
                    buf.write(s[:idx+1])
                    self._extra = s[idx+1:]
                    self._pos -= len(self._extra)
                    break
                elif idx > 0:
                    buf.write(s[:(size - written)])
                    self._extra = s[(size - written):]
                    self._pos -= len(self._extra)
                    break
                else:
                    buf.write(s)
                    written += len(s)
            except StopIteration:
                break

        return buf.getvalue()

    def readlines(self, sizehint=None):
        out = []

        if sizehint is None:
            s = self.readline()
            while len(s) > 0:
                out.append(s)
                s = self.readline()
            return out

        written = 0
        while written < sizehint:
            s = self.readline()
            if len(s) > 0 and len(s) <= (sizehint - written):
                out.append(s)
                written += len(s)
            elif len(s) > 0:
                if len(out) == 0:
                    out.append(s)
                    written += len(s)
                else:
                    self._extra = s + self._extra
                    self._pos -= len(s)
                    break
            else:
                break
        return out

    # xreadlines() not provided; deprecated
    # seek() not provided; "not all file objects are seekable"

    def tell(self):
        if self.closed:
            raise ValueError("file-like object is closed")
        return self._pos

    def truncate(self, size=None):
        raise IOError("File-like object not open for writing")

    def write(self, s):
        raise IOError("File-like object not open for writing")

    def writelines(self, seq):
        raise IOError("File-like object not open for writing")
    
    def __iter__(self):
        return StreamingSourceIterator(self)
