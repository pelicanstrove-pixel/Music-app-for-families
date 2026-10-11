%% Logs every note LilyPond performs (in the MIDI pass, so repeats are written out) to <file>-events.txt:
%%   N  staff voice moment duration grace midi step alter octave timesig measurePosition clef
%%   T  voice moment                       (a tie starts on the notes of this voice at this moment)
%%   K  moment sharps-or-flats              (key signature: +n sharps, -n flats)
%%   S                                      (a new \score begins: one movement)
%% Moments and durations are exact fractions of a whole note. Time signature, bar position and clef are read
%% at the end of each moment, after LilyPond has applied that moment's \time, \partial and \clef.
%% Used by scores/tools/mutopia_to_musicxml.py.
\version "2.24.0"

#(define (ev-file) (string-append (ly:parser-output-name) "-events.txt"))
#(define (ev-out . items)
   (let ((p (open-file (ev-file) "a")))
     (display (string-join (map (lambda (x) (ly:format "~a" x)) items) "\t") p)
     (newline p) (close p)))
#(define (frac m) (ly:format "~a/~a" (ly:moment-main-numerator m) (ly:moment-main-denominator m)))
#(define (ctx-key ctx) (if ctx (number->string (object-address ctx)) "?"))

#(define event-performer
   (lambda (context)
     (let ((pending '()))
       (make-performer
        (listeners
         ((note-event performer event)
          (let ((p (ly:event-property event 'pitch)))
            (if (ly:pitch? p) (set! pending (cons event pending)))))
         ((tie-event performer event)
          (ev-out "T" (ctx-key context) (frac (ly:context-current-moment context))))
         ((key-change-event performer event)
          (let* ((alist (ly:event-property event 'pitch-alist))
                 (alts (if (pair? alist) (filter (lambda (x) (not (zero? (cdr x)))) alist) '()))
                 (n (length alts)))
            (ev-out "K" (frac (ly:context-current-moment context))
                    (if (and (pair? alts) (negative? (cdr (car alts)))) (- n) n)))))
        ((stop-translation-timestep performer)
         (if (pair? pending)
             (let* ((now (ly:context-current-moment context))
                    (ts (ly:context-property context 'timeSignatureFraction))
                    (mp (ly:context-property context 'measurePosition))
                    (cg (ly:context-property context 'clefGlyph))
                    (staff (ly:context-find context 'Staff)))
               (for-each
                (lambda (event)
                  (let ((p (ly:event-property event 'pitch)))
                    (ev-out "N" (ctx-key staff) (ctx-key context) (frac now)
                            (frac (ly:duration-length (ly:event-property event 'duration)))
                            (if (zero? (ly:moment-grace-numerator now)) 0 1)
                            (+ 60 (ly:pitch-semitones p)) (ly:pitch-notename p)
                            (exact->inexact (ly:pitch-alteration p)) (ly:pitch-octave p)
                            (if (pair? ts) (ly:format "~a/~a" (car ts) (cdr ts)) "4/4")
                            (if (ly:moment? mp) (frac mp) "0/1")
                            (if (string? cg) cg "?"))))
                (reverse pending))
               (set! pending '()))))))))

#(define score-marker
   (lambda (context)
     (make-performer ((initialize translator) (ev-out "S")))))

\midi {
  \context { \Score \consists #score-marker }
  \context { \Voice \consists #event-performer }
}
