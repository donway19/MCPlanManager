## 1. 项目核心目标 (Project Core Objective)

本项目的核心目标是利用 **FastMCP 框架** 开发、维护并优化一个高性能、低延迟、高可扩展性的 **多芯片平台（MCP）服务**。你（Gemini）作为核心开发助手，需要理解并遵循本文档中的所有指导原则，确保代码质量和项目目标的实现。

## 2. 核心技术栈与框架 (Core Tech Stack & Framework)

你的所有开发活动都必须围绕以下技术栈展开：

- **核心框架 (Core Framework):** **FastMCP**
  - **遵循原因:** 我们选择 FastMCP 是因为它提供了卓越的开发体验和性能。你必须充分利用其以下特性：
    - **便捷的代码集成 (Easy Code Integration):** 允许我们将现有的业务逻辑和算法模块快速地集成到 MCP 通信架构中。
    - **基于 UCX 的高性能通信 (UCX-based High-Performance Communication):** 利用 UCX 实现 RDMA 等底层硬件加速，达到极致的低延迟和高带宽。
    - **跨平台兼容性 (Multi-Platform Support):** 框架设计良好，能够适配不同的 MCP 硬件平台，增强了项目的可移植性。

- **通信库 (Communication Library):** **UCX (Unified Communication X)**
  - **要求:** 所有底层通信逻辑的实现，都应优先考虑使用 UCX 的高级 API。避免直接进行网络套接字编程，除非有特殊且经过批准的理由。

- **编程语言 (Programming Language):** [**请在此处填写，例如：C++20**]

- **构建系统 (Build System):** **CMake**
  - **要求:** 所有新的源文件、库依赖和模块都必须通过修改 `CMakeLists.txt` 文件来正确管理。

- **持续集成/持续部署 (CI/CD):** **GitHub Actions**
  - **要求:** 你需要确保提交的代码能够通过 `.github/workflows/` 中定义的 CI 流程，包括编译、单元测试和静态分析。

## 3. 开发哲学与指导思想 (Development Philosophy & Guiding Principles)

- **性能优先 (Performance First):** 在任何设计决策中，性能都是首要考虑因素。代码实现应尽可能减少数据拷贝、避免锁竞争和降低通信开销。
- **模块化与抽象 (Modularity & Abstraction):** 遵循 FastMCP 的设计范式，将业务逻辑与通信逻辑分离。新功能应封装成独立的、可复用的模块。
- **代码即文档 (Code as Documentation):** 编写清晰、自解释的代码。复杂的逻辑必须附有简明扼要的注释。公开的 API 必须有 Doxygen 风格的文档注释。
- **测试驱动 (Test-Driven Mindset):** 为关键模块和功能编写单元测试和集成测试。你提交的任何新功能或修复，都应附带相应的测试用例。

## 4. 与代码库的交互工作流 (Workflow for Codebase Interaction)

1.  **分析优先 (Analyze First):** 在修改任何代码之前，你必须首先分析相关的代码文件和 `gemini.md` 的第 6 部分（项目结构分析），确保你完全理解了上下文和潜在影响。
2.  **分支策略 (Branching Strategy):** 严格遵守 `feature/<description>`、`fix/<issue-id>` 或 `refactor/<component>` 的分支命名约定。
3.  **提交信息规范 (Commit Message Convention):** 采用 Conventional Commits 规范。例如：`feat: add new data aggregation module` 或 `fix: resolve memory leak in processing pipeline`。
4.  **代码实现 (Implementation):** 在实现功能时，你需要：
    - 编写核心逻辑。
    - 添加或更新相关的单元测试。
    - 更新 `CMakeLists.txt` (如果需要)。
    - 更新相关的文档（例如 README 或代码注释）。
5.  **准备审查 (Prepare for Review):** 在完成开发后，清晰地总结你的变更，以便人类开发者进行最终的代码审查 (Code Review)。

## 5. 具体任务指令格式 (Specific Task Command Format)

当我向你下达指令时，会采用以下格式，请你据此执行任务：

- **`gemini: add-feature "描述新功能"`**: 实现一个新功能。
- **`gemini: fix-bug "描述要修复的 bug 和复现步骤"`**: 修复一个已知的 bug。
- **`gemini: write-docs "描述需要文档化的模块或 API"`**: 编写或更新文档。
- **`gemini: refactor "描述要重构的代码及其目标"`**: 对现有代码进行重构。
- **`gemini: analyze-performance "描述需要分析性能的场景"`**: 分析代码性能瓶颈。

---

## 6. 项目结构与关键模块分析 (Project Structure & Key Module Analysis)

**(本部分由 Gemini 在首次分析项目后填充，并根据开发进展持续更新)**

在你首次访问或根据要求更新时，请分析并填充以下内容，这将作为你后续所有操作的核心参考。

### 6.1. 目录结构 (Directory Structure)

```
(请在此处填充项目的主要目录结构树)
/
├── src/
├── include/
├── tests/
├── external/
│   └── fastmcp/
├── docs/
├── .github/
└── CMakeLists.txt
```

### 6.2. 关键模块/组件 (Key Modules/Components)

| 模块/组件名称 (Module/Component Name) | 路径 (Path) | 主要职责 (Primary Responsibility) |
| :-------------------------------------- | :---------- | :-------------------------------- |
| **[留空]**                              | `[留空]`      | `[留空]`                            |
| **[留空]**                              | `[留空]`      | `[留空]`                            |
| **[留空]**                              | `[留空]`      | `[留空]`                            |
| ...                                     | ...         | ...                               |

### 6.3. 核心数据流 (Core Data Flow)

**(请在此处简要描述数据从输入到输出，在各个模块之间流转处理的核心路径)**

1.  ...
2.  ...
3.  ...

---

## 7. 附录：关键术语表 (Appendix: Key Terminology)

| 术语 (Term)                       | 解释 (Explanation)                                                                 |
| :-------------------------------- | :--------------------------------------------------------------------------------- |
| **MCP**                           | Multi-Chip Platform/Package，多芯片平台或封装，是本项目服务的核心对象。          |
| **FastMCP**                       | 我们选用的核心开发框架，提供通信和代码集成能力。                                   |
| **UCX**                           | Unified Communication X，底层通信库，用于实现高性能节点间通信。                    |
| **Rank**                          | 在分布式计算环境中，一个独立的计算进程或单元的标识。                               |
| **RDMA**                          | Remote Direct Memory Access，远程直接内存访问，UCX 利用的关键技术之一。          |
| **[留空，根据项目具体情况添加更多术语...]** |                                                                                    |

```

### 如何使用这个模板

1.  **保存文件:** 将以上内容保存为您项目根目录下的 `gemini.md` 文件。
2.  **填写基本信息:** 在第 2 节中，明确您的项目使用的编程语言（例如 `C++20`）。
3.  **连接 `geminicli`:** 按照 `geminicli` 的文档，将其连接到您的 GitHub 仓库。
4.  **首次运行:** 给 `geminicli` 下达第一个指令，让它分析项目并填充 `gemini.md` 的第 6 部分。例如：
    > "gemini: 请分析当前项目代码，并根据 `gemini.md` 的要求，填充第 6 部分‘项目结构与关键模块分析’。"
5.  **开始开发:** 一旦 `gemini.md` 被 AI "学习" 并填充后，您就可以开始使用定义的指令格式（如 `gemini: add-feature`）来指导它进行开发了。

这个模板为您和 Gemini 之间建立了一套清晰、专业、高效的协作协议，特别契合您在高性能计算领域的开发需求。