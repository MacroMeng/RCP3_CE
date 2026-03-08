import pygame


def get_chinese_font(size, bold=False):
    if not bold:
        return pygame.font.Font('./fonts/MiSans-Regular.ttf', size)
    else:
        return pygame.font.Font('./fonts/MiSans-Bold.ttf', size)


def init():
    global MHicon, initbarsurface, screen, lastlength, init_background, mask, currentamount
    global choose_manager, drop_rate_manager, choose_mode, balance_weight, smart_sensitivity, enable_drop_rate

    # 第一次加载配置（不加载图片）
    load_config_to_globals('config.ini')

    if startwindowpositioncontrol:
        try:
            os.environ['SDL_VIDEO_WINDOW_POS'] = startwindowposition
        except:
            pass

    pygame.init()    # 初始化pygame
    screen = pygame.display.set_mode(
        (960, 540), RESIZABLE | HWSURFACE | DOUBLEBUF | SRCALPHA | NOFRAME
    )      # 界面大小
    pygame.display.set_caption(titleofprogramme)  # 标题
    pygame.display.set_icon(pygame.image.load('.\\images\\14.ico'))
    set_windows_taskbar_icon()

    itemscount = 7          # 要加载的项数

    # 随机选择背景图片
    init_bg_dir = globals().get(
        'init_bg_directory', './images/backgrounds/init_bg'
    )
    main_bg_dir = globals().get(
        'main_bg_directory', './images/backgrounds/main_bg'
    )
    use_random_bg = globals().get('use_random_bg', True)
    if use_random_bg:
        random_init_bg = get_random_image_from_directory(init_bg_dir)
        random_main_bg = get_random_image_from_directory(main_bg_dir)
        if random_init_bg:
            print(f'随机选择的载入界面背景: {random_init_bg}')
            globals()['init_background_path'] = random_init_bg
        else:
            globals()['init_background_path'] = init_background
            print('未找到随机载入界面背景，使用默认')
        if random_main_bg:
            print(f'随机选择的主界面背景: {random_main_bg}')
            globals()['background_img_path'] = random_main_bg
        else:
            globals()['background_img_path'] = background_img
            print('未找到随机主界面背景，使用默认')
    else:
        globals()['init_background_path'] = init_background
        globals()['background_img_path'] = background_img

    # 加载为pygame Surface对象
    globals()['init_background'] = pygame.image.load(init_background_path)
    globals()['background_image'] = pygame.image.load(background_img_path)
    globals()['MHicon'] = pygame.image.load(MHicon)

    # 缩放初始化背景
    try:
        init_background = pygame.transform.smoothscale(
            init_background,
            (
                int(
                    init_background.get_width()
                    * max(
                        screen.get_width() / init_background.get_width(),
                        screen.get_height() / init_background.get_height(),
                    )
                ),
                int(
                    init_background.get_height()
                    * max(
                        screen.get_width() / init_background.get_width(),
                        screen.get_height() / init_background.get_height(),
                    )
                ),
            ),
        )
    except:
        if use_random_bg:
            init_bg_dir = globals().get(
                'init_bg_directory', './images/backgrounds/init_bg'
            )
            random_init_bg = get_random_image_from_directory(init_bg_dir)

            if random_init_bg:
                print(f'随机选择的载入界面背景: {random_init_bg}')
                globals()['init_background_path'] = random_init_bg
            else:
                globals()['init_background_path'] = init_background
                print('未找到随机载入界面背景，使用默认')

        else:
            globals()['init_background_path'] = init_background

        init_background = pygame.transform.smoothscale(
            init_background,
            (
                int(
                    init_background.get_width()
                    * max(
                        screen.get_width() / init_background.get_width(),
                        screen.get_height() / init_background.get_height(),
                    )
                ),
                int(
                    init_background.get_height()
                    * max(
                        screen.get_width() / init_background.get_width(),
                        screen.get_height() / init_background.get_height(),
                    )
                ),
            ),
        )

    screen.blit(init_background, (0, 0))
    mask = pygame.Surface(
        (screen.get_width(), screen.get_height()), SRCALPHA | HWSURFACE
    )
    mask.fill((0, 0, 0, init_background_alpha))

    # 缩放MHicon
    MHicon = pygame.transform.smoothscale(
        MHicon,
        (int(MHicon.get_width() * 0.08), int(MHicon.get_height() * 0.08)),
    )
    mask.blit(MHicon, ((mask.get_width() - MHicon.get_width()) / 2, 0))
    MHtext = get_chinese_font(size=int(33)).render(' ', True, (255, 255, 255))
    mask.blit(
        MHtext,
        (
            (mask.get_width() - MHtext.get_width()) / 2 + 10,
            MHicon.get_height() - 25,
        ),
    )
    screen.blit(mask, (0, 0))
    pygame.display.flip()
    pygame.time.Clock().tick(1)

    screen.blit(init_background, (0, 0))
    softwaretext = get_chinese_font(size=int(40), bold=True).render(
        packagename, True, (255, 255, 255)
    )
    mask.blit(
        softwaretext,
        (
            (mask.get_width() - softwaretext.get_width()) / 2,
            MHicon.get_height() + MHtext.get_height() - 25,
        ),
    )
    versiontext = get_chinese_font(size=int(20), bold=True).render(
        version, True, (255, 255, 255)
    )
    mask.blit(
        versiontext,
        (
            (mask.get_width() - softwaretext.get_width()) / 2
            + softwaretext.get_width()
            + 10,
            MHicon.get_height()
            + MHtext.get_height()
            - 25
            + softwaretext.get_height()
            - versiontext.get_height(),
        ),
    )
    screen.blit(mask, (0, 0))
    pygame.display.flip()
    pygame.time.Clock().tick(30)
    screen.blit(init_background, (0, 0))
    initbarsurface = pygame.Surface(
        (screen.get_width(), screen.get_height()), SRCALPHA
    )
    pygame.draw.rect(
        mask,
        (127, 127, 127, 180),
        (
            (screen.get_width() - 720) / 2,
            screen.get_height() / 2 + 150,
            720,
            5,
        ),
        border_radius=2,
    )
    screen.blit(mask, (0, 0))
    pygame.display.flip()
    lastlength = 0
    currentamount = 0
    globals()['init_fpsk'] = init_fps / 360
    for i in range(itemscount):       # 载入内容的循环
        init_items(i, itemscount, 100, animation)   # 加载的某一项
        pygame.event.get()
    screen.blit(init_background, (0, 0))
    screen.blit(mask, (0, 0))
    loadingpercent = get_chinese_font(size=int(15)).render(
        ('100.00%'), True, (255, 255, 255)
    )
    screen.blit(
        loadingpercent,
        ((screen.get_width() - 720) / 2 + 730, screen.get_height() / 2 + 140),
    )
    ldtext = '已完成！正在载入……'
    loadingtext = get_chinese_font(size=int(15)).render(
        ldtext, True, (255, 255, 255)
    )
    screen.blit(
        loadingtext,
        ((screen.get_width() - 720) / 2, screen.get_height() / 2 + 160),
    )
    if animation:
        for i in range(int(63 * init_fpsk)):
            pygame.draw.rect(
                initbarsurface,
                (0, 191, 0, int(4 / init_fpsk)),
                (
                    (screen.get_width() - 720) / 2,
                    screen.get_height() / 2 + 150,
                    720,
                    5,
                ),
                border_radius=2,
            )
            screen.blit(initbarsurface, (0, 0))
            pygame.display.flip()
            pygame.time.Clock().tick(init_fps)
    else:
        pygame.draw.rect(
            screen,
            (0, 191, 0, 255),
            (
                (screen.get_width() - 720) / 2,
                screen.get_height() / 2 + 150,
                720,
                5,
            ),
            border_radius=2,
        )
        pygame.display.flip()
        pygame.time.Clock().tick(init_fps)
    tempsurface = pygame.Surface(
        (screen.get_width(), screen.get_height()), SRCALPHA
    )
    pygame.draw.rect(
        tempsurface,
        (0, 0, 0, int(10 / init_fpsk)),
        (0, 0, tempsurface.get_width(), tempsurface.get_height()),
    )
    for i in range(int(63 * init_fpsk)):
        screen.blit(tempsurface, (0, 0))
        pygame.display.flip()
        pygame.time.Clock().tick(init_fps)
    screen = pygame.display.set_mode(
        screensize, RESIZABLE | HWSURFACE | DOUBLEBUF | SRCALPHA
    )
    pygame.time.Clock().tick(init_fps)
    backgroundimage = proportional_scale(
        background_image, window_width, window_height
    )
    global tempsurface_2
    tempsurface_2 = pygame.Surface(
        (screen.get_width(), screen.get_height()), SRCALPHA
    )
    tempsurface_2.blit(backgroundimage, (0, 0))
    global lastname
    lastname = firstdraw_lastname
    draw_lastname(flush=False, temp=True)
    lastmessage = welcomemessage
    message(lastmessage, flush=False, temp=True)
    draw_button(
        (
            int((window_width - 100 * k) / 2),
            int((window_height - 30 * k) / 2 + 200 * k),
        ),
        (100 * k, 30 * k),
        '抽选',
        rad=int(3 * k),
        color=(15, 15, 15),
        _alpha_=180,
        temp=True,
    )
    fullscreenbutton(flush=False, temp=True)
    settingsbutton(flush=False, temp=True)
    for i in range(int(63 * init_fpsk)):
        tempsurface.fill((0, 0, 0, 0))
        screen.blit(tempsurface_2, (0, 0))
        showclock(flush=False)
        pygame.draw.rect(
            tempsurface,
            (0, 0, 0, int(255 - 4 * i / init_fpsk)),
            (0, 0, tempsurface.get_width(), tempsurface.get_height()),
        )
        screen.blit(tempsurface, (0, 0))
        pygame.display.flip()
        pygame.time.Clock().tick(init_fps)

    # 初始化点名管理器
    try:
        from choose_manager import choose_manager

        print('✅ 点名管理器初始化成功')
    except Exception as e:
        print(f'❌ 点名管理器初始化失败: {e}')
        # 创建临时的空管理器
        class DummyManager:
            def __init__(self):
                self.history_data = {}
                self.today_data = {}

            def record_choice(self, name):
                pass

            def get_choice_count(self, name, mode):
                return 0

            def clear_history(self):
                pass

            def clear_today(self):
                pass

        choose_manager = DummyManager()

    # 初始化爆率管理器 - 修复这里！
    try:
        from drop_rate_manager import drop_rate_manager

        # drop_rate_manager 在初始化时已经自动加载数据，不需要再次调用
        print('✅ 爆率管理器初始化成功')
    except Exception as e:
        print(f'❌ 爆率管理器初始化失败: {e}')
        # 创建临时的空管理器 - 修复这个类！
        class DummyDropManager:
            def __init__(self):
                self.auto_rates = {}
                self.manual_rates = {}

            def get_drop_rate(self, name, use_manual_override=True):
                return 1.0

            def set_drop_rate(self, name, rate, is_manual=True):
                return True

            def update_from_list(self, name_list):
                return False, []

            def reset_drop_rate(self, name):
                return True

            def reset_all_drop_rates(self):
                return True

        drop_rate_manager = DummyDropManager()

    print(
        f'📝 点名模式: {choose_mode}, 平衡权重: {balance_weight}, 智能敏感度: {smart_sensitivity}, 启用爆率: {enable_drop_rate}'
    )

    # 根据初始名单更新爆率配置
    if enable_drop_rate and _name_:
        drop_rate_manager.update_from_list(_name_)
        print('✅ 爆率配置已根据名单更新')

    globals()['sleep_time'] = time.time()
    function_loader(func_file='rootmainloop.py')
    rootmainloop()


def init_items(num, total, totalamount, animation):
    global initbarsurface, lastlength, currentamount, namelist, _name_, init_fpsk
    currentlength = lastlength
    match num:
        case 0:
            global except_name, time, threading, random, copy, datetime, tk, buttonx, buttony, sizex, sizey, fps, used_times, screen, is_fullscreen, barsurface, buttonsurface, window_width, window_height, k, version, screen, clock, settings_img, bar_screen, background_img, name, clocksurface, namesurface
            globals()['reset_namelist'] = 0
            globals()['message_time'] = 0
            globals()['dpup'] = 0
            globals()['used_times'] = 0
            globals()['sleep_time'] = 0
            currentamount += 5
            screen.blit(init_background, (0, 0))
            screen.blit(mask, (0, 0))
            ldtext = '载入全局变量……'
            loadingtext = get_chinese_font(size=int(15)).render(
                ldtext, True, (255, 255, 255)
            )
            screen.blit(
                loadingtext,
                (
                    (screen.get_width() - 720) / 2,
                    screen.get_height() / 2 + 160,
                ),
            )
        case 1:
            import time
            import threading
            import random
            import copy
            import datetime

            used_times = 0
            is_fullscreen = False
            # 删除这里的背景加载代码，因为已经在 config_loader 中加载了
            # try:
            #     globals()['background_image']=pygame.image.load(background_img).convert_alpha()
            # except:
            #     pass
            currentamount += 33
            screen.blit(init_background, (0, 0))
            screen.blit(mask, (0, 0))
            ldtext = '读取背景……'
            loadingtext = get_chinese_font(size=int(15)).render(
                ldtext, True, (255, 255, 255)
            )
            screen.blit(
                loadingtext,
                (
                    (screen.get_width() - 720) / 2,
                    screen.get_height() / 2 + 160,
                ),
            )
        case 2:
            pygame.display.set_caption(titleofprogramme)  # 标题
            try:
                pygame.display.set_icon(pygame.image.load('.\\images\\14.ico'))
            except:
                pass
            currentamount += 3
            screen.blit(init_background, (0, 0))
            screen.blit(mask, (0, 0))
            ldtext = '设定窗口……'
            loadingtext = get_chinese_font(size=int(15)).render(
                ldtext, True, (255, 255, 255)
            )
            screen.blit(
                loadingtext,
                (
                    (screen.get_width() - 720) / 2,
                    screen.get_height() / 2 + 160,
                ),
            )
        case 3:
            (
                window_width,
                window_height,
            ) = pygame.display.get_surface().get_size()
            _k_()
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
            globals()['settingbutton_img'] = pygame.transform.smoothscale(
                pygame.image.load('.\\images\\buttons\\settings.png'),
                (int(36 * k), int(36 * k)),
            )
            currentamount += 7
            screen.blit(init_background, (0, 0))
            screen.blit(mask, (0, 0))
            ldtext = '计算比例系数……'
            loadingtext = get_chinese_font(size=int(15)).render(
                ldtext, True, (255, 255, 255)
            )
            screen.blit(
                loadingtext,
                (
                    (screen.get_width() - 720) / 2,
                    screen.get_height() / 2 + 160,
                ),
            )
        case 4:
            namesurface = pygame.Surface(
                (4.5 * 150 * k + 30 * k, 150 * k + 60 * k),
                SRCALPHA | HWSURFACE,
            )
            pygame.draw.rect(
                namesurface,
                (0, 0, 0, 155),
                (0, 0, 4.5 * 150 * k + 30 * k, 150 * k + 60 * k),
                border_radius=int(33 * k),
            )
            clocksurface = pygame.Surface(
                (140 * k, 40 * k), SRCALPHA | HWSURFACE
            )
            buttonsurface = pygame.Surface(
                (100 * k, 30 * k), SRCALPHA | HWSURFACE
            )
            globals()['settingsurface'] = pygame.Surface(
                (36 * k, 36 * k), SRCALPHA | HWSURFACE
            )
            barsurface = pygame.Surface((0, 0), SRCALPHA | HWSURFACE)
            pygame.draw.rect(
                clocksurface,
                (0, 0, 0, 100),
                (0, 0, 130 * k, 40 * k),
                border_radius=int(5 * k),
            )
            currentamount += 32
            screen.blit(init_background, (0, 0))
            screen.blit(mask, (0, 0))
            ldtext = '创建表面……'
            loadingtext = get_chinese_font(size=int(15)).render(
                ldtext, True, (255, 255, 255)
            )
            screen.blit(
                loadingtext,
                (
                    (screen.get_width() - 720) / 2,
                    screen.get_height() / 2 + 160,
                ),
            )
        case 5:
            buttonx = int((window_width - 100 * k) / 2)
            buttony = int((window_height - 30 * k) / 2 + 200 * k)
            sizex = int(100 * k)
            sizey = int(30 * k)
            currentamount += 6
            screen.blit(init_background, (0, 0))
            screen.blit(mask, (0, 0))
            ldtext = '创建变量……'
            loadingtext = get_chinese_font(size=int(15)).render(
                ldtext, True, (255, 255, 255)
            )
            screen.blit(
                loadingtext,
                (
                    (screen.get_width() - 720) / 2,
                    screen.get_height() / 2 + 160,
                ),
            )
        case 6:

            def read_name_file(filepath, default_error):
                if not os.path.exists(filepath):
                    print(f'文件不存在: {filepath}')
                    return [default_error]
                encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16', 'latin-1']
                for encoding in encodings:
                    try:
                        with open(filepath, 'r', encoding=encoding) as f:
                            result = [
                                line.strip() for line in f if line.strip()
                            ]
                        if result:
                            print(f'成功使用 {encoding} 编码读取: {filepath}')
                            return result
                    except (UnicodeDecodeError, Exception) as e:
                        continue
                try:
                    with open(
                        filepath, 'r', encoding='utf-8', errors='ignore'
                    ) as f:
                        result = [line.strip() for line in f if line.strip()]
                    print(f'使用错误忽略模式读取: {filepath}')
                    return result
                except Exception as e:
                    print(f'读取文件失败 {filepath}: {e}')
                    return [default_error]

            _name_ = read_name_file(name_text, 'error0001')
            if _name_ == ['error0001']:
                print('主名单加载错误')
            except_name = read_name_file(except_names, 'error0002')
            if except_name == ['error0002']:
                print('排除名单加载错误')
            currentamount += 14
            screen.blit(init_background, (0, 0))
            screen.blit(mask, (0, 0))
            ldtext = '读取名单和功能模块……'
            loadingtext = get_chinese_font(size=int(15)).render(
                ldtext, True, (255, 255, 255)
            )
            screen.blit(
                loadingtext,
                (
                    (screen.get_width() - 720) / 2,
                    screen.get_height() / 2 + 160,
                ),
            )
            function_loader(func_file='rootmainloop.py')
            function_loader(func_file='buttons.py')
            function_loader(func_file='choice_logic.py')
            function_loader(func_file='animation.py')
            function_loader(func_file='exitwindow.py')
            function_loader(func_file='pack_up.py')
            function_loader(func_file='floatingbutton.py')
            function_loader(func_file='sleep.py')
            function_loader(func_file='choose_manager.py')
            function_loader(func_file='drop_rate_manager.py')
    if animation:
        if currentlength < 4:
            currentlength = 4
        screen.blit(init_background, (0, 0))
        screen.blit(mask, (0, 0))
        loadingtext = get_chinese_font(size=int(15)).render(
            ldtext, True, (255, 255, 255)
        )
        screen.blit(
            loadingtext,
            ((screen.get_width() - 720) / 2, screen.get_height() / 2 + 160),
        )
        pygame.draw.rect(
            screen,
            (255, 255, 255, 255),
            (
                (screen.get_width() - 720) / 2,
                screen.get_height() / 2 + 150,
                currentlength,
                5,
            ),
            border_radius=2,
        )
        loadingpercent = get_chinese_font(size=int(15)).render(
            (str('%.2f' % (currentlength * 100 / 720)) + '%'),
            True,
            (255, 255, 255),
        )
        screen.blit(
            loadingpercent,
            (
                (screen.get_width() - 720) / 2 + 730,
                screen.get_height() / 2 + 140,
            ),
        )
        pygame.display.flip()
        while currentlength < 720 * (currentamount) / totalamount:
            screen.blit(init_background, (0, 0))
            screen.blit(mask, (0, 0))
            pygame.draw.rect(
                screen,
                (255, 255, 255, 255),
                (
                    (screen.get_width() - 720) / 2,
                    screen.get_height() / 2 + 150,
                    currentlength,
                    5,
                ),
                border_radius=2,
            )
            loadingpercent = get_chinese_font(size=int(15)).render(
                (str('%.2f' % (currentlength * 100 / 720)) + '%'),
                True,
                (255, 255, 255),
            )
            screen.blit(
                loadingpercent,
                (
                    (screen.get_width() - 720) / 2 + 730,
                    screen.get_height() / 2 + 140,
                ),
            )
            currentlength += int(animationspeed / init_fpsk)
            pygame.display.update((0, 415, 960, 15))
            pygame.time.Clock().tick(init_fps)
        lastlength = currentlength
    else:
        screen.blit(init_background, (0, 0))
        screen.blit(mask, (0, 0))
        loadingtext = get_chinese_font(size=int(15)).render(
            ldtext, True, (255, 255, 255)
        )
        screen.blit(
            loadingtext,
            ((screen.get_width() - 720) / 2, screen.get_height() / 2 + 160),
        )
        pygame.draw.rect(
            screen,
            (255, 255, 255, 255),
            (
                (screen.get_width() - 720) / 2,
                screen.get_height() / 2 + 150,
                currentlength,
                5,
            ),
            border_radius=2,
        )
        loadingpercent = get_chinese_font(size=int(15)).render(
            (str('%.2f' % (currentlength * 100 / 720)) + '%'),
            True,
            (255, 255, 255),
        )
        screen.blit(
            loadingpercent,
            (
                (screen.get_width() - 720) / 2 + 730,
                screen.get_height() / 2 + 140,
            ),
        )
        pygame.draw.rect(
            screen,
            (255, 255, 255, 255),
            (
                (screen.get_width() - 720) / 2,
                screen.get_height() / 2 + 150,
                720 / totalamount * (currentamount),
                5,
            ),
            border_radius=2,
        )
        pygame.display.flip()
    if 720 / total * (num + 1) < 720:
        pygame.time.Clock().tick(15)
    else:
        pygame.time.Clock().tick(init_fps)


def set_windows_taskbar_icon():
    """使用Windows API设置任务栏图标"""
    try:
        import ctypes

        # 获取当前窗口句柄
        hwnd = pygame.display.get_wm_info()['window']

        # 设置窗口类名（重要！）
        class_name = titleofprogramme.replace(' ', '_')

        # 加载图标
        ICON_SMALL = 0  # 小图标（16x16）
        ICON_BIG = 1    # 大图标（32x32）

        # 从文件加载图标
        icon_path = '.\\images\\14.ico'

        # 使用LoadImage加载图标
        LR_LOADFROMFILE = 0x00000010
        hicon = ctypes.windll.user32.LoadImageW(
            0, icon_path, 1, 0, 0, LR_LOADFROMFILE  # IMAGE_ICON
        )

        if hicon:
            # 设置窗口图标
            ctypes.windll.user32.SendMessageW(
                hwnd, 0x80, ICON_SMALL, hicon  # WM_SETICON
            )

            ctypes.windll.user32.SendMessageW(
                hwnd, 0x80, ICON_BIG, hicon  # WM_SETICON
            )

            # 强制窗口重绘
            ctypes.windll.user32.RedrawWindow(
                hwnd,
                None,
                None,
                0x85,  # RDW_FRAME | RDW_ERASE | RDW_INVALIDATE
            )

            print('✅ Windows任务栏图标已设置')
            return True
    except Exception as e:
        print(f'❌ Windows API图标设置失败: {e}')

    return False
