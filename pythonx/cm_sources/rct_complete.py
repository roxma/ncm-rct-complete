# -*- coding: utf-8 -*-

from cm import register_source, getLogger, Base

register_source(name='rct-complete',
                priority=9,
                abbreviation='rb',
                scoping=True,
                scopes=['ruby'],
                sort=0,
                cm_refresh_patterns=[r'\.$'],)

import subprocess

logger = getLogger(__name__)

class Source(Base):

    def __init__(self,nvim):
        super(Source,self).__init__(nvim)

        try:
            from distutils.spawn import find_executable
            # echoe does not work here
            if not find_executable("rct-complete"):
                self.message('error', "Can't find [rct-complete] binary. Please install rcodetools https://rubygems.org/gems/rcodetools")
        except:
            pass


    def cm_refresh(self,info,ctx,*args):

        src = self.get_src(ctx)

        # use stdin for rct-complete
        proc = subprocess.Popen(args=['rct-complete',
            '--completion-class-info',
            '--dev',
            '--fork',
            '--line=%s' % ctx['lnum'],
            '--column=%s' % (ctx['col']-1),
            '--filename=%s' % ctx['filepath']
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL)

        result, errs = proc.communicate(src.encode('utf-8'),timeout=30)
        logger.debug("result %s", result)

        result = result.decode('utf-8')

        results = result.split("\n")
        if not results:
            return

        matches = []
        for line in results:

            # sayHi\tHelloWorld#sayHi
            fields = line.split("\t")
            if not fields:
                continue

            word = fields[0]
            menu = ''
            if len(fields)>1:
                menu = fields[1]

            if not word.strip():
                continue

            item = dict(word=word,
                        icase=1,
                        dup=1,
                        menu=menu,
                        )

            matches.append(item)

        logger.debug('matches %s', matches)
        self.complete(info, ctx, ctx['startcol'], matches)

