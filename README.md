
# 🚀 AlgoFlow: C++ 算法练习自动构建系统

一个为算法练习设计的 **跨平台自动化开发脚本**，支持一键编译、调试、测试、管理工具模块和题目模板，助你高效刷题！

---

## 📋 功能概览 🛠️

| 功能               | 描述                                                                   |
| ------------------ | ---------------------------------------------------------------------- |
| 🧱 **项目初始化**   | `init` 初始化基础目录结构和工具模板                                    |
| 📄 **题目管理**     | `new <name>` 创建新题 / `delete <name>` 删除题目                       |
| 🛠️ **工具模块管理** | `util <name> --add` 添加工具模块 / `util <name> --remove` 删除工具模块 |
| 🧪 **编译与调试**   | 支持 `--mode debug/release`、GDB 调试、自动运行程序                    |
| 📝 **测试用例管理** | 支持录制输入输出为测试样例，自动对比测试结果并标红差异                 |
| 🧹 **构建清理**     | `clean` 清空编译输出目录                                               |

---

## 📦 目录结构 📁

```bash
project/
├── build/           # 编译输出目录
├── src/             # 题目源文件目录
│   └── 001.cpp      # 示例题目源文件
├── tools/           # 工具函数目录
│   ├── utils.h      # 工具函数头文件（自动包含新增模块）
│   ├── utils.cpp
│   ├── logger.h     # 新增的工具模块示例
│   └── logger.cpp
├── test_cases/      # 测试用例目录
│   └── 001/
│       ├── input_0.txt
│       └── output_0.txt
├── build.py         # Python 构建脚本 🐍
```

---

## 🧪 快速开始 🚀

### 0. 获取帮助 📕
```bash
python build.py help
```

### 1. 初始化项目 🧱

```bash
python build.py init
```

### 2. 创建新题目 📄

```bash
python build.py new t_001
```

### 3. 编译并调试 🛠️

```bash
python build.py compile t_001 --mode debug --gdb
```

### 4. 增加测试用例 📝

```bash
python build.py test t_001 --record
```

### 5. 运行测试并对比结果 🧪

```bash
python build.py test t_001
```

### 6. 删除题目 🗑️

```bash
python build.py delete t_001
```

### 7. 管理工具模块 🔧

```bash
# 添加工具模块
python build.py util logger --add

# 删除工具模块
python build.py util logger --remove
```

---

## 🎯 命令详解 📚

### `init`
初始化项目目录结构和基础工具文件（`tools/utils.cpp`，`tools/utils.cpp`）。

### `new <name>`
创建新题目的源文件（`src/<name>.cpp`）和测试用例目录（`test_cases/<name>/`）。

### `compile <name> [--mode debug/release] [--run] [--gdb]`
编译指定题目，支持：
- `--mode`：选择 `debug`（默认）或 `release` 模式
- `--run`：编译后运行程序
- `--gdb`：启动 GDB 调试器

### `run <name>`
运行程序。

### `gdb <name>`
在 GDB 调试器中调试程序。

### `test <name> [--record]`
自动运行所有保存的测试用例，对比输出结果并标红差异 ⚠️。
- `--record`：运行程序并记录输入输出为测试样例

### `delete <name>`
删除题目源文件和测试用例目录。

### `clean [name]`
清空 `build/` 目录。

若 `[name]` 不为空，则清空 `build/` 目录中所有和 `[name]` 相关的文件。

### `add-util <name>`
创建工具模块的 `.h` 和 `.cpp` 文件，并在 `tools/utils.h` 中自动添加 `#include`。

### `remove-util <name>`
删除工具模块文件，并从 `tools/utils.h` 中移除对应的 `#include` 行。

---

## 🧩 技术亮点 💡

- ✅ **单文件**：只由一个 `build.py` 文件构成 📌
- ✅ **零依赖**：仅使用 Python 标准库 🐍
- ✅ **工具模块化**：每个工具独立成文件，通过 `utils.h` 统一管理 🧩
- ✅ **测试自动化**：支持录制和对比测试用例，差异标红 🔴
- ✅ **多测试用例支持**：测试用例支持多个输入输出文件（自动编号 `input_0.txt`, `input_1.txt`...）📄

---

## 📄 许可证 📜

该项目采用 MIT License，请自由使用和修改 ✅

---

## 🙌 致谢 ❤️

感谢你的使用！如果你觉得这个项目有帮助，欢迎 Star ⭐ 和分享给其他人 🙏
