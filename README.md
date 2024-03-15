# find_lib

在不知道函数定义的时候，寻找函数的库。

usage:
```bash
$ python3 match.py -E /bin/ls -L /lib/x86_64-linux-gnu/ -F exit
exit is defined in /lib/x86_64-linux-gnu/libc.so.6
```

原理

动态链接库名称：

ELF文件中 `dynamic` 区包含需要的动态库
- `DT_NEEDED`: 所需要的动态库，`d_val` 指向字符表的下标（字符表由DT_STRTAB确定）

寻找so：`nm -D xxx.so`，其中，-D表示显示动态符号表，-T代表Text段


todo
- [ ] match 改为pyelftools实现
- [ ] ida python