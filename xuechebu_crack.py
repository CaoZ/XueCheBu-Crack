import getpass
import sys

import os

import requests

USER = ['驾校帐号', '密码']
USER_INFO_CORRECT = True


def get_unfinished_list(session):
    url = 'http://xcbapi.xuechebu.com/videoApi/video/GetChapterList?os=pc'

    unfinished = []

    try:
        r = session.get(url)
        data = get_response_data(r)

        subject = data[0]  # 科目1
        # subject = data[1]  # 科目3
        classes = subject['ClassList']

        for a_class in classes:
            print('# {}:'.format(a_class['ClassName']))

            for a_chapter in a_class['ChapterList']:
                print('## ' + a_chapter['ChapterName'], end=' ')
                finished = a_chapter['SFJS'] == '1'
                finished_txt = '已学' if finished else '未学'
                print(finished_txt)

                if not finished:
                    unfinished.append(a_chapter)

        return unfinished

    except Exception as e:
        print('获取应学课程出错: ' + str(e))


def finish_chapter(session, chapter):
    url = 'http://xcbapi.xuechebu.com/videoApi/student/UpdatePlay'

    data = {
        'os': 'pc',
        'type': 4,
        'id': chapter['ID'],  # 课程视频 id
        'beforeWatchTime': 1,
        'thisWatchTime': chapter['SPSC']  # 视频时长
    }

    print('学习中...')

    try:
        r = session.post(url, data)
        data = get_response_data(r)

        chapter_finished = data['SFJS'] == '1'
        class_finished = data['KSSFJS'] == '1'

        print('章节: {}; 章节完成: {}; 课时完成: {}'.format(chapter['ID'], chapter_finished, class_finished))

    except Exception as e:
        print('标记出错, 章节: {}.'.format(chapter['ID']))


def get_should_chapter(session):
    url = 'http://xcbapi.xuechebu.com/videoApi/video/GetShouldChapter?os=pc'

    try:
        r = session.get(url)
        data = get_response_data(r)

        print('该学 {} {} 了.'.format(data['KSMC'], data['ZJMC']))
        return True

    except Exception as e:
        print('获取应学章节出错: ' + str(e))
        return False


def login(session, username, password):
    url = 'http://api.xuechebu.com/user/stulogin'

    data = {
        'username': username,
        'password': password,
        'os': 'pc'
    }

    try:
        r = session.post(url, data)
        data = get_response_data(r)

        print('登录成功! 姓名: {}, 驾校: {}.'.format(data['xm'], data['jxmc']))
        return True

    except Exception as e:
        print('登录失败: ' + str(e))
        return False


def get_response_data(response):
    try:
        response.raise_for_status()
        as_json = response.json()

    except requests.HTTPError as e:
        raise Exception('请求出错: ' + str(e))

    except Exception as e:
        raise Exception(e)

    if as_json['code'] == 0:
        return as_json['data']

    else:
        raise Exception('请求出错: ' + as_json['message'])


def main():
    print('来来来~ 上课啦~\n')

    try:
        print('(ง •̀_•́)ง \n')
    except UnicodeEncodeError as e:
        # 在 Windows 上的 cmd 中打印不出以上颜文字, 因 stdout 的编码是 gbk ...
        pass

    session = requests.session()

    while True:
        user = get_user()

        succeed = login(session, *user)

        if not succeed:
            print('登录失败~ 请重试.\n')
            global USER_INFO_CORRECT
            # 登录失败, 可能是帐号或密码错误, 后面只尝试从 stdin 中读取数据
            USER_INFO_CORRECT = False

        else:
            print()
            break

    unfinished = get_unfinished_list(session)

    print()

    if unfinished is None:
        # error occurred
        return

    can_learn = get_should_chapter(session)

    if can_learn:
        print()
        for a_chapter in unfinished:
            finish_chapter(session, a_chapter)

    print('\n恭喜~ 已完成今天的学习~\n')
    print('[]~(￣▽￣)~* \n')

    if os.name == 'nt':
        # 在 Windows 上提示 '请按任意键继续. . .' 而不是一闪而过的退出
        os.system('pause')


def get_user():
    user = []

    if USER_INFO_CORRECT:
        # 默认传入或内置的 user_info 是正确的, 读取它们的值
        if len(sys.argv) == 3:
            user = [sys.argv[1], sys.argv[2]]

        else:
            user = USER

    while not (user and is_valid_username(user[0])):
        username = input('请输入驾校帐号: ')
        password = getpass.getpass('请输入密码: ')
        user = [username, password]

        if is_valid_username(username):
            break

        else:
            print('帐号似乎有误, 请重新输入.\n')

    return user


def is_valid_username(username):
    # 驾校帐号一般是身份证, 而身份证可能以 X 结尾
    return username[:-1].isdigit()


if __name__ == '__main__':
    main()
