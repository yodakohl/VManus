EVA_VISUAL_COMPONENTS: Dict[str, Dict[str, str]] = {
    # bench / loop-onset glyphs
    'o':     {'first_stroke': 'loop',       'last_stroke': 'loop',       'glyph_class': 'bench'},
    'a':     {'first_stroke': 'loop',       'last_stroke': 'tail',       'glyph_class': 'bench'},
    'e':     {'first_stroke': 'loop',       'last_stroke': 'loop',       'glyph_class': 'bench'},
    'r':     {'first_stroke': 'loop',       'last_stroke': 'sigmoid',    'glyph_class': 'bench'},
    'l':     {'first_stroke': 'loop',       'last_stroke': 'vertical',   'glyph_class': 'bench'},
    # ligatures with loop onset
    'al':    {'first_stroke': 'loop',       'last_stroke': 'vertical',   'glyph_class': 'bench'},
    'ol':    {'first_stroke': 'loop',       'last_stroke': 'vertical',   'glyph_class': 'bench'},
    'ar':    {'first_stroke': 'loop',       'last_stroke': 'sigmoid',    'glyph_class': 'bench'},
    'or':    {'first_stroke': 'loop',       'last_stroke': 'sigmoid',    'glyph_class': 'bench'},
    'ey':    {'first_stroke': 'loop',       'last_stroke': 'descender',  'glyph_class': 'bench'},
    'aiin':  {'first_stroke': 'loop',       'last_stroke': 'hook',       'glyph_class': 'bench'},
    'aiiin': {'first_stroke': 'loop',       'last_stroke': 'hook',       'glyph_class': 'bench'},
    # gallows / ascender-onset glyphs
    'k':     {'first_stroke': 'ascender',   'last_stroke': 'ascender',   'glyph_class': 'gallows'},
    't':     {'first_stroke': 'ascender',   'last_stroke': 'crossbar',   'glyph_class': 'gallows'},
    'p':     {'first_stroke': 'ascender',   'last_stroke': 'plume',      'glyph_class': 'gallows'},
    'f':     {'first_stroke': 'ascender',   'last_stroke': 'crossbar',   'glyph_class': 'gallows'},
    'g':     {'first_stroke': 'vertical',   'last_stroke': 'ascender',   'glyph_class': 'minim'},
    # minim / vertical-onset glyphs
    'i':     {'first_stroke': 'vertical',   'last_stroke': 'vertical',   'glyph_class': 'minim'},
    'm':     {'first_stroke': 'vertical',   'last_stroke': 'vertical',   'glyph_class': 'minim'},
    'd':     {'first_stroke': 'vertical',   'last_stroke': 'vertical',   'glyph_class': 'minim'},
    'n':     {'first_stroke': 'vertical',   'last_stroke': 'hook',       'glyph_class': 'minim'},
    'iin':   {'first_stroke': 'vertical',   'last_stroke': 'hook',       'glyph_class': 'minim'},
    'iiin':  {'first_stroke': 'vertical',   'last_stroke': 'hook',       'glyph_class': 'minim'},
    # suffix / descender glyphs
    'y':     {'first_stroke': 'ascender',   'last_stroke': 'descender',  'glyph_class': 'suffix'},
    'dy':    {'first_stroke': 'vertical',   'last_stroke': 'descender',  'glyph_class': 'suffix'},
    'q':     {'first_stroke': 'ascender',   'last_stroke': 'descender',  'glyph_class': 'suffix'},
    # compound glyphs
    'qo':    {'first_stroke': 'ascender',   'last_stroke': 'loop',       'glyph_class': 'compound'},
    'qot':   {'first_stroke': 'ascender',   'last_stroke': 'crossbar',   'glyph_class': 'compound'},
    'qok':   {'first_stroke': 'ascender',   'last_stroke': 'ascender',   'glyph_class': 'compound'},
    # c/h family (open_curve / sigmoid onset)
    'c':     {'first_stroke': 'open_curve', 'last_stroke': 'open_curve', 'glyph_class': 'bench'},
    'h':     {'first_stroke': 'open_curve', 'last_stroke': 'connector',  'glyph_class': 'bench'},
    'ch':    {'first_stroke': 'open_curve', 'last_stroke': 'connector',  'glyph_class': 'bench'},
    'sh':    {'first_stroke': 'sigmoid',    'last_stroke': 'connector',  'glyph_class': 'bench'},
    'cth':   {'first_stroke': 'open_curve', 'last_stroke': 'connector',  'glyph_class': 'bench'},
    'ckh':   {'first_stroke': 'open_curve', 'last_stroke': 'connector',  'glyph_class': 'bench'},
    'cph':   {'first_stroke': 'open_curve', 'last_stroke': 'connector',  'glyph_class': 'bench'},
    'cfh':   {'first_stroke': 'open_curve', 'last_stroke': 'connector',  'glyph_class': 'bench'},
    's':     {'first_stroke': 'sigmoid',    'last_stroke': 'sigmoid',    'glyph_class': 'bench'},
    # rare glyphs
    'v':     {'first_stroke': 'open_curve', 'last_stroke': 'hook',       'glyph_class': 'rare'},
    'z':     {'first_stroke': 'sigmoid',    'last_stroke': 'hook',       'glyph_class': 'rare'},
    'x':     {'first_stroke': 'crossbar',   'last_stroke': 'crossbar',   'glyph_class': 'rare'},
    # connector-onset glyphs
    'b':     {'first_stroke': 'connector',  'last_stroke': 'connector',  'glyph_class': 'bench'},
    'j':     {'first_stroke': 'connector',  'last_stroke': 'connector',  'glyph_class': 'bench'},
    'u':     {'first_stroke': 'connector',  'last_stroke': 'connector',  'glyph_class': 'bench'},
}
