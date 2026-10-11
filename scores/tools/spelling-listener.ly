%% Writes every note's written spelling (letter, accidental, octave) and its MIDI number to
%% <file>-spelling.txt, so a MIDI file made by LilyPond can be turned into MusicXML with the
%% typesetter's own spelling. Used by scores/tools/mutopia_to_musicxml.py.
\version "2.24.0"
#(define (spelling-file) (string-append (ly:parser-output-name) "-spelling.txt"))
#(define (log-pitch engraver event)
   (let ((p (ly:event-property event 'pitch)))
     (if (ly:pitch? p)
         (let ((port (open-file (spelling-file) "a")))
           (display (ly:format "~a\t~a\t~a\t~a\n"
                               (+ 60 (ly:pitch-semitones p))
                               (ly:pitch-notename p)
                               (exact->inexact (ly:pitch-alteration p))
                               (ly:pitch-octave p)) port)
           (close port)))))
#(define spelling-engraver
   (make-engraver (listeners ((note-event engraver event) (log-pitch engraver event)))))
\layout { \context { \Voice \consists #spelling-engraver } }
