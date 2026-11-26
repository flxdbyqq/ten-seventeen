# 《十点十七分》 第一章《迟到》
# Ren'Py 8.6.1

init python:
    renpy.music.register_channel("ambient", mixer="sfx", loop=True)
    renpy.music.register_channel("ticks", mixer="sfx", loop=True)
    renpy.music.register_channel("sfx", mixer="sfx", loop=False)
    renpy.music.register_channel("typing", mixer="sfx", loop=False)
    renpy.music.register_channel("typewriter", mixer="sfx", loop=False)
    renpy.music.register_channel("riser", mixer="sfx", loop=False)
    renpy.music.register_channel("ring", mixer="sfx", loop=False)

    def case_line(t, s):
        return "{font=fonts/SpecialElite-Regular.ttf}" + t + "{/font}　" + s

    def _speaker_sprites(kind):
        """只有正在说话的人出现：主角左，司仪右，旁白/画外音两边都不出现。"""
        def callback(event, interact=True, **kwargs):
            if event != "begin":
                return
            scene = getattr(renpy.store, "sprite_scene", "hall")
            if scene == "hall":
                if kind == "miles":
                    if not renpy.showing("miles_idle"):
                        renpy.show("miles_idle", at_list=[miles_left])
                    renpy.hide("char_director")
                    renpy.hide("miles_paper")
                elif kind == "officiant":
                    if not renpy.showing("char_director"):
                        renpy.show("char_director", at_list=[director_right])
                    renpy.hide("miles_idle")
                    renpy.hide("miles_paper")
                else:
                    renpy.hide("miles_idle")
                    renpy.hide("miles_paper")
                    renpy.hide("char_director")
            else:
                renpy.hide("miles_idle")
                renpy.hide("miles_paper")
                renpy.hide("char_director")
        return callback


define white_flash = Fade(0.06, 0.0, 0.35, color="#ffffff")

define officiant = Character("司仪", who_color="#b9b2a6", what_color="#e8e2d6",
                             callback=_speaker_sprites("officiant"))
define miles = Character(None, what_color="#d8d3c8", what_italic=True,
                         callback=_speaker_sprites("miles"))
define miles_speak = Character("莫罗", who_color="#d8d3c8", what_color="#e8e2d6",
                               callback=_speaker_sprites("miles"))
define eulogy = Character("画外音", who_color="#7d766b", what_color="#8f877a", what_italic=True,
                          callback=_speaker_sprites("none"))
define c = Character(None, what_style="centered_text", window_style="centered_window",
                     what_font="fonts/LXGWWenKaiLite-Regular.ttf", what_size=26,
                     what_color="#d8d3c8", callback=_speaker_sprites("none"))

image bg_hall = Transform("images/bg/bg_hall_wide.png", xysize=(1280, 720), fit="cover")
image bg_coffin = Transform("images/bg/bg_coffin_close.png", xysize=(1280, 720), fit="cover")
image char_director = "images/characters/director/director_default.png"
image miles_idle = "images/characters/miles/miles_idle.png"
image miles_paper = "images/characters/miles/miles_paper.png"
image miles_portrait = "images/characters/miles/miles_portrait.png"
image miles_face = "images/characters/miles/miles_face.png"
image ui_vignette = "images/placeholder/vignette.png"
image ui_grain = "images/placeholder/grain.png"

default case_time = "10:17"
default sprite_scene = "hall"
default saw_body = False
default smoked = False
default coffin_start = 0.0
default coffin_seconds = 0

transform kenburns:
    xalign 0.5
    yalign 0.5
    zoom 1.0
    linear 30.0 zoom 1.05

transform miles_left:
    alpha 0.0
    xalign 0.12
    yalign 1.0
    yzoom 0.32
    xzoom 0.32
    linear 0.16 alpha 1.0

transform director_right:
    alpha 0.0
    xalign 0.86
    yalign 1.0
    yzoom 0.50
    xzoom 0.50
    linear 0.16 alpha 1.0

transform vignette_breathe:
    alpha 0.55
    linear 2.2 alpha 0.85
    linear 2.2 alpha 0.55
    repeat

transform grain_flicker:
    alpha 1.0
    linear 0.08 alpha 0.7
    linear 0.12 alpha 1.0
    pause 0.05
    repeat

transform blink:
    alpha 0.25
    linear 1.0 alpha 0.9
    linear 1.0 alpha 0.25
    repeat

transform face_flash:
    xalign 0.5
    yalign 0.42
    zoom 1.15

transform violent_shake:
    subpixel True
    transform_anchor True
    xanchor 0.5
    yanchor 0.5
    xpos 0.5
    ypos 0.5
    zoom 1.10
    offset (0, 0)
    linear 0.03 offset (-34, -20)
    linear 0.03 offset (30, 18)
    linear 0.03 offset (-26, 22)
    linear 0.03 offset (34, -16)
    linear 0.03 offset (-20, -22)
    linear 0.03 offset (26, 16)
    linear 0.03 offset (-18, 12)
    linear 0.03 offset (12, -10)
    linear 0.04 offset (-8, 6)
    linear 0.05 offset (0, 0)

transform stamp_in:
    alpha 0.0
    zoom 1.8
    linear 0.12 alpha 1.0 zoom 1.0


screen timestamp():
    zorder 100
    hbox:
        xalign 0.97
        yalign 0.035
        spacing 8
        text "●" color "#e8a24a" size 10 at blink
        text case_time font "fonts/SpecialElite-Regular.ttf" size 18 color "#8a8378"


screen case_file(lines, show_stamp=False):
    zorder 50
    add "images/ui/paper.png"
    vbox:
        xpos 140
        ypos 100
        spacing 12
        for line in lines:
            text line size 22 color "#1a1816" font "fonts/LXGWWenKaiLite-Regular.ttf"
    if show_stamp:
        fixed:
            xpos 760
            ypos 430
            xsize 300
            ysize 300
            at stamp_in
            add "images/ui/stamp_ring.png"
            text "已记录" xalign 0.5 yalign 0.5 color "#8b2e2a" size 42 font "fonts/ZCOOLXiaoWei-Regular.ttf" at Transform(rotate=-8)


label start:
    $ quick_menu = False
    show screen timestamp
    scene black
    $ sprite_scene = "cold"
    $ case_time = "10:17"
    play ambient "audio/rain.wav" fadein 2.0 volume 0.6
    play ticks "audio/clock.wav" loop volume 0.35
    pause 1.0

    c "人在迟到的时候，会想很多理由。"
    c "我想不出。"
    c "她在里面等我。已经等了一辈子。"
    c "不差这十七分钟。"

    play sfx "audio/door.wav" volume 0.8
    pause 0.7
    play sfx "audio/footsteps_hall.wav" volume 0.95
    pause 2.6

    stop ticks
    stop ambient
    play sfx "audio/match.wav" volume 0.8
    scene bg_hall at kenburns
    $ sprite_scene = "hall"
    show ui_vignette at vignette_breathe
    show ui_grain at grain_flicker
    with Dissolve(1.5)
    play ambient "audio/drone.wav" loop fadein 1.5 volume 0.5

    officiant "您迟到了。"
    miles "他记得很清楚。比我还清楚。"

    $ case_time = "10:23"
    officiant "仪式已经开始了。您迟到了十七分钟。"
    officiant "按照流程，您需要先确认遗体，然后在确认单上签字。"
    miles "流程。母亲活着的时候，最讨厌流程。"
    officiant "外面雨很大。需要毛巾吗？"
    miles_speak "不用。"
    miles "她以前总说，淋了雨要换衣服。现在没人说了。"
    officiant "请节哀。"
    miles "他说得很客气，像在念一份使用说明。"

    eulogy "她是一位伟大的母亲。她把一生都奉献给了家庭。"
    miles "她不识字。这两个字，她大概不认识。"
    eulogy "我们会永远怀念她。"
    miles "她最讨厌别人替她总结一生。"

    $ case_time = "10:42"
    scene bg_coffin at kenburns
    $ sprite_scene = "hall"
    show ui_vignette at vignette_breathe
    show ui_grain at grain_flicker
    with Dissolve(1.2)
    stop ticks
    stop ambient
    play ambient "audio/heartbeat.wav" loop fadein 2.0 volume 0.55
    $ coffin_start = renpy.get_game_runtime()

    officiant "Please confirm."
    officiant "请确认遗体。"
    miles "白纱下面是她。我看不清她。"
    miles "她也看不清我。"

    hide miles_idle
    hide char_director
    menu:
        "掀开白纱。":
            $ saw_body = True
            jump look_body
        "就这样站着。":
            $ saw_body = False
            jump dont_look


label look_body:
    miles "我掀开白纱。"
    stop ambient
    window hide
    hide miles_idle
    hide char_director
    play riser "audio/rumble_riser.wav" volume 0.55
    play sfx "audio/candle.wav" volume 0.5
    show miles_face at face_flash
    pause 0.18
    hide miles_face
    pause 0.6
    with white_flash
    stop riser
    play sfx "audio/impact.wav" volume 1.0
    play ring "audio/tinnitus.mp3" volume 0.5
    show layer master at violent_shake
    $ renpy.pause(0.6, hard=True)
    show layer master
    pause 0.6
    miles "白纱下面的人，是我。"
    miles "我笑了一下。不是故意的。"
    stop ring fadeout 2.2
    play ambient "audio/drone.wav" loop fadein 2.0 volume 0.45
    officiant "莫罗先生？"
    miles_speak "……没事。"
    jump after_coffin


label dont_look:
    miles "我站着。没有动。"
    officiant "我理解。"
    officiant "但流程需要您确认。"
    miles "他替我看了。"
    stop ambient
    window hide
    hide miles_idle
    hide char_director
    play riser "audio/rumble_riser.wav" volume 0.55
    play sfx "audio/candle.wav" volume 0.5
    show miles_face at face_flash
    pause 0.18
    hide miles_face
    pause 0.6
    with white_flash
    stop riser
    play sfx "audio/impact.wav" volume 1.0
    play ring "audio/tinnitus.mp3" volume 0.5
    show layer master at violent_shake
    $ renpy.pause(0.6, hard=True)
    show layer master
    pause 0.6
    miles "白纱下面的人，是我。"
    stop ring fadeout 2.2
    play ambient "audio/drone.wav" loop fadein 2.0 volume 0.45
    officiant "莫罗先生？"
    miles_speak "……没事。"
    jump after_coffin


label after_coffin:
    $ coffin_seconds = max(1, int(renpy.get_game_runtime() - coffin_start))
    officiant "请签字。"
    play sfx "audio/pen.wav" volume 0.7
    pause 0.8

    hide screen timestamp
    stop ambient
    scene black
    play sfx "audio/impact.wav" volume 0.8
    pause 0.4

    show text "{font=fonts/SpecialElite-Regular.ttf}{size=96}{color=#e8e2d6}10:17{/color}{/size}{/font}" at truecenter with Dissolve(1.0)
    pause 1.2
    hide text with Dissolve(0.4)
    show text "{font=fonts/SpecialElite-Regular.ttf}{size=54}{color=#e8e2d6}TEN SEVENTEEN{/color}{/size}\n{font=fonts/LXGWWenKaiLite-Regular.ttf}{size=22}{color=#b9b2a6}第一章　迟到{/color}{/size}" at truecenter with Dissolve(1.0)
    pause 2.2
    hide text with Dissolve(1.0)

    show screen timestamp
    $ case_time = "10:47"
    scene bg_hall at kenburns
    $ sprite_scene = "hall"
    show ui_vignette at vignette_breathe
    show ui_grain at grain_flicker
    with Dissolve(1.2)
    play ambient "audio/drone.wav" loop fadein 2.0 volume 0.5

    officiant "仪式还有二十分钟。您可以到外面抽支烟。"
    miles "灵堂门口贴着“禁止吸烟”。"
    miles "他大概没看见。"

    hide miles_back
    hide char_director
    menu:
        "接过烟。":
            $ smoked = True
            jump smoke
        "摇头。":
            $ smoked = False
            jump no_smoke


label smoke:
    play sfx "audio/match.wav" volume 0.8
    pause 0.3
    play sfx "audio/exhale.wav" volume 0.7
    miles "第一口烟下去，我才想起来，我已经三天没睡了。"
    officiant "您母亲不喜欢烟味。"
    miles_speak "我知道。"
    officiant "……请节哀。"
    jump casefile


label no_smoke:
    miles "我把手插回口袋。口袋里有一盒烟。"
    officiant "您口袋里有烟。"
    miles_speak "嗯。"
    officiant "……请节哀。"
    jump casefile


label casefile:
    hide screen timestamp
    stop ambient
    window hide
    scene black
    $ sprite_scene = "none"
    play typewriter "audio/typewriter.wav" volume 0.85 fadein 0.3
    $ clines = []
    show screen case_file(clines)
    $ clines.append("{font=fonts/SpecialElite-Regular.ttf}{size=28}MORROW, MILES{/size}{/font}")
    show screen case_file(clines)
    pause 0.4
    $ clines.append("{font=fonts/SpecialElite-Regular.ttf}{size=16}ATTENDANCE RECORD — 10:17{/size}{/font}")
    show screen case_file(clines)
    pause 0.6
    $ clines.append("")
    show screen case_file(clines)
    pause 0.3

    $ clines.append(case_line("10:17", "被告迟到。"))
    show screen case_file(clines)
    pause 0.5

    $ clines.append(case_line("10:23", "被告未更换湿外套。"))
    show screen case_file(clines)
    pause 0.5

    if saw_body:
        $ clines.append(case_line("10:42", "被告瞻仰遗容，停留 %d 秒。" % coffin_seconds))
    else:
        $ clines.append(case_line("10:42", "被告拒绝瞻仰遗容。"))
    show screen case_file(clines)
    pause 0.5

    if smoked:
        $ clines.append(case_line("10:47", "被告在灵堂吸烟。"))
    else:
        $ clines.append(case_line("10:47", "被告拒绝香烟，但口袋内有烟盒。"))
    show screen case_file(clines)
    pause 0.5

    $ clines.append(case_line("10:58", "被告未流泪。"))
    show screen case_file(clines)
    pause 0.5

    $ clines.append(case_line("11:03", "被告微笑。"))
    show screen case_file(clines)
    stop typewriter fadeout 0.6
    play typing "audio/typing.mp3" volume 0.6 fadein 0.2
    pause 2.6

    play sfx "audio/stamp.wav" volume 0.9
    show screen case_file(clines, show_stamp=True)
    pause 1.8
    stop typing fadeout 0.8

    hide screen case_file
    scene black
    show text "{font=fonts/LXGWWenKaiLite-Regular.ttf}{size=34}{color=#d8d3c8}第一章《迟到》　完{/color}{/size}{/font}" at truecenter with Dissolve(1.0)
    pause 2.4
    hide text with Dissolve(0.6)
    play sfx "audio/page_turn.wav" volume 0.6
    show text "{font=fonts/ZCOOLXiaoWei-Regular.ttf}{size=60}{color=#e8e2d6}《局外人》{/color}{/size}{/font}" at truecenter with Dissolve(1.4)
    pause 3.0
    return

label debug_hall:
    $ quick_menu = False
    show screen timestamp
    $ case_time = "10:23"
    scene bg_hall at kenburns
    $ sprite_scene = "hall"
    show ui_vignette at vignette_breathe
    show ui_grain at grain_flicker
    with Dissolve(0.5)
    officiant "您迟到了。"
    miles "他记得很清楚。比我还清楚。"
    pause

label debug_choices:
    $ quick_menu = False
    show screen timestamp
    $ case_time = "10:42"
    scene bg_hall at kenburns
    $ sprite_scene = "hall"
    show ui_vignette at vignette_breathe
    show ui_grain at grain_flicker
    with Dissolve(0.5)
    menu:
        "掀开白纱。":
            pass
        "就这样站着。":
            pass
    pause
