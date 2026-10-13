# -*- coding: utf-8 -*-
"""核验 _旧版/ 副本完整性；若与根目录同名文件一致，则清除根目录冗余副本。"""
import os
import hashlib

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '01-工蜂产出')
OLD = os.path.join(BASE, '_旧版')


def md5(p, step=1 << 20):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        while True:
            b = f.read(step)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def main():
    root_pdfs = sorted(f for f in os.listdir(BASE) if f.lower().endswith('.pdf'))
    old_pdfs = set(f for f in os.listdir(OLD) if f.lower().endswith('.pdf'))

    for f in root_pdfs:
        rp = os.path.join(BASE, f)
        op = os.path.join(OLD, f)
        rs = os.path.getsize(rp)
        if f not in old_pdfs:
            print('[KEEP ] %-34s %7.1f MB  (旧版无副本)' % (f, rs / 1048576))
            continue
        os_ = os.path.getsize(op)
        if rs != os_:
            print('[KEEP ] %-34s 大小不一致 root=%.1f old=%.1f MB' % (f, rs / 1048576, os_ / 1048576))
            continue
        a, b = md5(rp), md5(op)
        if a != b:
            print('[KEEP ] %-34s md5 不一致' % f)
            continue
        print('[DUP  ] %-34s %7.1f MB  md5=%s  _旧版已有同源副本' % (f, rs / 1048576, a[:10]))
        try:
            os.remove(rp)
            print('        -> 已删除根目录冗余副本')
        except OSError as e:
            print('        -> 删除失败(环境拦截): %s' % e)

    print('-' * 58)
    for n in sorted(os.listdir(BASE)):
        q = os.path.join(BASE, n)
        if os.path.isdir(q):
            sz = sum(os.path.getsize(os.path.join(r, x)) for r, _, fs in os.walk(q) for x in fs)
            cnt = sum(len(fs) for _, _, fs in os.walk(q))
            print('[D] %-8s %7.1f MB  (%d files)' % (n, sz / 1048576, cnt))
        else:
            print('[F] %-8s %7.1f MB' % (n, os.path.getsize(q) / 1048576))


if __name__ == '__main__':
    main()
