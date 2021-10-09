M107               ; turn off filament cooling fan
M140 S70           ; set bed temp
M104 S180          ; set hot end temp
M105               ; report temps
M190 S70           ; wait for bed
M105               ; report temps
M109 S210          ; wait for hot end
M82                ; absolute extrusion mode
G90                ; absolute positioning mode
G21                ; use metric values
G28                ; home axes
G92 E0             ; reset filament position
G1 Y0.15           ; move head to belt
G1 X200 E50 F800   ; extruder purge line
G1 Z0.3            ; shift belt away 0.3mm
G1 X0 E100         ; extruder purge line
G92 Z0 E0          ; reset bed + extruder position
M117 CR-30 Printing...
G1 E-6.0000 F4200 ; e-retract 6
