def animation_choice():
    global name, fpsk, kkk, lastlengthofbar, dpup, namesurface, used_times, fps, buttonx, buttony, sizex, sizey, lastname, k, window_width, window_height, lastname
    global lastmessage, buttonx, buttony, sizex, sizey, k, window_width, window_height, lastname, bg, background_img, message_time, ww, wh, animation, fullscreensurface, clocksurface, namesurface, buttonsurface, barsurface, screen, is_fullscreen
    current_time_seconds = time.time()
    lastlengthofbar = 0
    background()
    draw_button(
        (buttonx, buttony),
        (sizex, sizey),
        '正在抽选',
        rad=int(3 * k),
        color=(15, 15, 15),
        _alpha_=180,
    )
    pygame.display.update(
        (
            int((window_width - 100 * k) / 2),
            int((window_height - 30 * k) / 2 + 200 * k),
            100 * k,
            30 * k,
        )
    )

    fpsk = fps / 180
    a = 0
    kkk = 0.75

    if k <= 0:
        k = 1.0

    base_fps = fps
    tempfps = int(base_fps * 3 / kkk)

    tempfps = max(30, min(tempfps, 120))

    print(f'动画FPS: {tempfps}, k值: {k}')

    fullscreenbutton('disable')
    settingsbutton()
    message(lastmessage)
    dpup = 0

    for i in range(int(240 * fpsk * kkk)):
        background()
        if (
            time.time() - message_time >= message_time_length
            and message_time != 0
        ):
            lastmessage = ''
            message(lastmessage)
            message_time = 0
        if a % (6 * fpsk) == 0:
            showclock()
            # 动画过程中不记录历史
            lastname = randomchoice(record_history=False)
        bar(k * 3 * i / kkk / fpsk, 720 * k)

        event_listening([])
        if time.time() - dpup >= 0 and time.time() - dpup <= 1 and dpup != 0:
            buttonx, buttony = int((window_width - 100 * k) / 2), int(
                (window_height - 30 * k) / 2 + 200 * k
            )
            sizex, sizey = int(100 * k), int(30 * k)
            draw_button(
                (
                    int((window_width - 100 * k) / 2),
                    int((window_height - 30 * k) / 2 + 200 * k),
                ),
                (100 * k, 30 * k),
                '正在抽选',
                rad=int(3 * k),
                color=(15, 15, 15),
                _alpha_=180,
            )
            global fullscreensurface, exitfullscreenbutton_img, fullscreenbutton_img
            fullscreensurface = pygame.Surface((36 * k, 36 * k), SRCALPHA)
            fullscreenbutton_img = pygame.transform.smoothscale(
                pygame.image.load('.\\images\\buttons\\fullscreen.png'),
                (int(36 * k), int(36 * k)),
            )
            exitfullscreenbutton_img = pygame.transform.smoothscale(
                pygame.image.load('.\\images\\buttons\\exitfullscreen.png'),
                (int(36 * k), int(36 * k)),
            )
            globals()['settingsurface'] = pygame.Surface(
                (36 * k, 36 * k), SRCALPHA
            )
            globals()['settingbutton_img'] = pygame.transform.smoothscale(
                pygame.image.load('.\\images\\buttons\\settings.png'),
                (int(36 * k), int(36 * k)),
            )
            message(lastmessage, flush=False)
            showclock(flush=False)
            fullscreenbutton(flush=False)
            settingsbutton(flush=False)
            bar(k * 3 * i / kkk / fpsk, 720 * k)
            pygame.display.flip()
            dpup = 0
        a = a + 1
        pygame.time.Clock().tick(tempfps)
    background()
    # 只有最终结果才记录历史
    lastname = randomchoice(record_history=True)
    name.remove(lastname)
    used_times = used_times + 1
    bar_gone(720 * k)


def bar(lenth, total):
    global k, window_width, window_height, barsurface, lastlengthofbar, barspeed
    barsurface = pygame.Surface((total, 5 * k), SRCALPHA)
    deltalenth = k * barspeed / kkk / fpsk
    while lastlengthofbar <= lenth:
        pygame.draw.rect(
            barsurface,
            (200, 200, 200, 255),
            (0, 0, lastlengthofbar, 5 * k),
            border_radius=int(2 * k),
        )
        screen.blit(
            barsurface,
            ((window_width - total) / 2, window_height / 2 + 130 * k),
        )
        pygame.display.update(
            (window_width - total) / 2,
            window_height / 2 + 130 * k,
            total,
            5 * k,
        )
        lastlengthofbar += deltalenth
        pygame.time.Clock().tick(int(fps * k * 3 / kkk))
    pygame.draw.rect(
        barsurface,
        (200, 200, 200, 255),
        (0, 0, lenth, 5 * k),
        border_radius=int(2 * k),
    )
    screen.blit(
        barsurface, ((window_width - total) / 2, window_height / 2 + 130 * k)
    )


def bar_gone(total):
    global lastmessage, dpup, buttonx, buttony, sizex, sizey, k, window_width, window_height, barsurface, fps, buttonx, buttony, sizex, sizey, k, window_width, window_height, lastname, bg, background_img, used_times, message_time, ww, wh, animation, fullscreensurface, clocksurface, namesurface, buttonsurface, barsurface, screen, is_fullscreen
    fpsk = fps / 120
    x = (window_width - total) / 2
    y = window_height / 2 + 130 * k
    barsurface = pygame.Surface((total, 5 * k), SRCALPHA)
    for i in range(int(64 * fpsk)):
        background()
        showclock()
        if pygame.mouse.get_pos()[0] in range(
            int(window_width - 36 * k), window_width
        ) and pygame.mouse.get_pos()[1] in range(
            int(window_height - 36 * k), window_height
        ):
            fullscreenbutton('puton')
        else:
            fullscreenbutton()
        if (
            time.time() - message_time >= message_time_length
            and message_time != 0
        ):
            lastmessage = ''
            message(lastmessage)
            message_time = 0
        barsurface.fill((0, 0, 0, 0))
        pygame.draw.rect(
            barsurface,
            (200, 200, 200, int(255 - i * 4 / fpsk)),
            (0, 0, total, 5 * k),
            border_radius=int(2 * k),
        )
        screen.blit(barsurface, (x, y))
        pygame.display.update((x, y, total, 5 * k))
        event_listening(['bar_gone'])
        if time.time() - dpup >= 0.01 and time.time() - dpup <= 1:
            background()
            x = (window_width - total) / 2
            y = window_height / 2 + 130 * k
            screen.blit(barsurface, (x, y))
            (
                window_width,
                window_height,
            ) = pygame.display.get_surface().get_size()
            k = _k_()
            buttonx = int((window_width - 100 * k) / 2)
            buttony = int((window_height - 30 * k) / 2 + 200 * k)
            sizex = int(100 * k)
            sizey = int(30 * k)
            draw_lastname()
            global fullscreensurface, exitfullscreenbutton_img, fullscreenbutton_img
            fullscreensurface = pygame.Surface((36 * k, 36 * k), SRCALPHA)
            fullscreenbutton_img = pygame.transform.smoothscale(
                pygame.image.load('.\\images\\buttons\\fullscreen.png'),
                (int(36 * k), int(36 * k)),
            )
            exitfullscreenbutton_img = pygame.transform.smoothscale(
                pygame.image.load('.\\images\\buttons\\exitfullscreen.png'),
                (int(36 * k), int(36 * k)),
            )
            globals()['settingsurface'] = pygame.Surface(
                (36 * k, 36 * k), SRCALPHA
            )
            globals()['settingbutton_img'] = pygame.transform.smoothscale(
                pygame.image.load('.\\images\\buttons\\settings.png'),
                (int(36 * k), int(36 * k)),
            )
            fullscreenbutton()
            settingsbutton()
            message(lastmessage)
            showclock()
            draw_button(
                (buttonx, buttony),
                (sizex, sizey),
                '正在抽选',
                rad=int(3 * k),
                color=(15, 15, 15),
                _alpha_=180,
            )
            pygame.display.flip()
            dpup = 0
        pygame.time.Clock().tick(fps)
    background()
    barsurface.fill((0, 0, 0, 0))
    pygame.draw.rect(
        barsurface, (200, 200, 200, 0), (0, 0, total, 5 * k), border_radius=2
    )
    screen.blit(barsurface, (x, y))
    pygame.display.update((x, y, total, 5 * k))
