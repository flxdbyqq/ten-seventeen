# 《十点十七分》第一章音效清单（耳聆网）

原则：
- 只要**音效**，不要音乐、不要带台词的录音。
- 环境音要**可循环**；动作音要**干声 + 自然尾音**，大厅回声我们自己加。
- 优先 CC0 / 可商用 / 无需署名；下载**原始文件**，不要录屏或转录音质。
- 放到 `E:\aiproject\new\风格\音效原始\`，文件名按下表；我统一降噪、裁剪、循环、转 WAV。
- 规格：WAV / 48kHz / 24bit 最佳；44.1kHz / 16bit 也可以。

## 一、环境音（循环）

| 优先级 | 文件名 | 场景 | 时长 | 耳聆网搜索词 | 备注 |
|---|---|---|---|---|---|
| P0 | `rain.wav` | 开场、全场底 | 20–30s | 大雨 窗外 室内 雨声 循环 无雷 | 要“隔着墙听到的雨”，不要雷声、不要雨滴打在麦克风上 |
| P0 | `drone.wav` | 大厅 / 灵堂 | 20–30s | 空旷 房间 底噪 室内 环境音 大厅 | 极安静的房间音，带一点低频和远处混响；不要空调嗡嗡声太明显 |
| P0 | `clock.wav` | 开场 / 灵堂 | 15–30s | 老式 挂钟 秒针 滴答 循环 | 慢、稳、轻；不要电子表 |
| P1 | `candle.wav` | 棺材 / 幻觉 | 8–15s | 烛火 燃烧 火苗 轻微 循环 | 很近、很轻的火苗声；不要篝火 |
| P1 | `cry.wav` | 悼词段落 | 15–30s | 远处 抽泣 哭声 压抑 女声 无台词 | 要“隔着一排椅子听到的”，不能抢台词；不要嚎啕 |

## 二、动作音（单次）

| 优先级 | 文件名 | 场景 | 时长 | 耳聆网搜索词 | 备注 |
|---|---|---|---|---|---|
| P0 | `door.wav` | 开场进门 | 2–4s | 木门 关闭 沉重 回声 礼堂 | 低频多一点；后面会加混响 |
| P0 | `footsteps.wav` | 开场走近 | 3–5s | 皮鞋 脚步 空旷 走廊 回声 慢 | 单人、慢步、硬地；不要多人 |
| P0 | `match.wav` | 点蜡烛 / 点烟 | 0.5–1.5s | 火柴 划燃 特写 | 干声、近场；不要打火机 |
| P0 | `paper.wav` | 确认单 / 案卷 | 0.5–1.5s | 纸张 翻动 文件 沙沙 | 单张厚纸，不要翻书 |
| P0 | `pen.wav` | 签字 | 1–2s | 钢笔 签字 写字 划纸 | 金属笔尖划纸，清晰但不刺耳 |
| P0 | `stamp.wav` | 盖章 | 0.5–1.5s | 印章 盖章 砸下 木质 沉重 | 要有桌面共振；这是全片最重的一下 |
| P0 | `heartbeat.wav` | 棺材前 | 5–10s | 心跳 缓慢 低沉 闷 循环 | 慢、闷、贴耳；不要恐怖片式急促 |
| P0 | `impact.wav` | 闪脸 / 震屏 | 1–3s | 低频 轰鸣 耳鸣 冲击 心跳停止 电影 | 不要金属撞击；要“轰”一下然后迅速收掉 |
| P1 | `exhale.wav` | 抽烟分支 | 1–2s | 叹气 吐气 烟 呼吸 | 近场、克制；不要咳嗽 |
| P2 | `chair.wav` | 坐下 / 起身 | 0.5–1.5s | 木椅 吱呀 轻响 | 很轻，可选 |
| P2 | `cloth.wav` | 转身 / 坐下 | 0.5–1.5s | 西装 布料 摩擦 衣服 | 很轻，可选 |

## 三、界面音（可选，但很提质感）

| 优先级 | 文件名 | 场景 | 时长 | 耳聆网搜索词 | 备注 |
|---|---|---|---|---|---|
| P2 | `ui_select.wav` | 选择确认 | 0.1–0.3s | 木头 轻敲 点击 轻响 | 不要“叮”的电子音；像手指敲一下桌面 |
| P2 | `ui_back.wav` | 回退 / 取消 | 0.1–0.3s | 纸张 轻响 翻页 短 | 可选 |

## 英文补充搜索（Freesound 等）

`heavy rain indoors loop no thunder` / `empty hall room tone` / `grandfather clock ticking loop` / `distant crying woman no dialogue` / `candle flame loop` / `wooden door close hall reverb` / `leather shoes footsteps hall reverb` / `match strike close` / `paper shuffle single sheet` / `fountain pen writing paper` / `rubber stamp thud wood desk` / `slow muffled heartbeat loop` / `cinematic low boom tinnitus` / `exhale smoke close`.

## 下载后

把文件丢到 `E:\aiproject\new\风格\音效原始\`，告诉我一声。我会：
1. 统一转 48kHz WAV、响度对齐；
2. 环境音做无缝循环；
3. 动作音裁掉头尾静音、加淡入淡出；
4. 放进 `game/audio/`，接进 `script.rpy` 和设置里的音量。
