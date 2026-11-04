# Issue tracker：本地 Markdown

本仓库的 issue 和规格存放在 `.scratch/` 下的 Markdown 文件中。

## 约定

- 每个功能一个目录：`.scratch/<feature-slug>/`。
- 规格文件：`.scratch/<feature-slug>/spec.md`。
- 实现 issue：`.scratch/<feature-slug>/issues/<NN>-<slug>.md`；从 `01` 开始编号，每个 issue 单独成文件。
- 在 issue 文件顶部附近用 `Status:` 记录 triage 状态；状态字符串见 `docs/agents/triage-labels.md`。
- 在文件末尾的 `## Comments` 标题下追加评论和交流记录。

## 当 skill 要求“publish to the issue tracker”

在 `.scratch/<feature-slug>/` 下创建文件；目录不存在时先创建。

## 当 skill 要求“fetch the relevant ticket”

读取所引用路径下的文件。用户通常会提供路径或 issue 编号。

## Wayfinding 操作

供 `/wayfinder` 使用。Map 是一个文件，每个 child ticket 是单独的文件。

- **Map**：`.scratch/<effort>/map.md`，正文包含 Notes、Decisions-so-far 和 Fog。
- **Child ticket**：`.scratch/<effort>/issues/NN-<slug>.md`，从 `01` 开始编号；正文写明问题。`Type:` 记录 `research`、`prototype`、`grilling` 或 `task`；`Status:` 记录 `claimed` 或 `resolved`。
- **阻塞关系**：文件顶部附近用 `Blocked by: NN, NN` 记录。所有列出的 ticket 均为 `resolved` 时解除阻塞。
- **Frontier**：扫描 `.scratch/<effort>/issues/`，选择编号最小、未认领、未解决且未被阻塞的 ticket。
- **认领**：开始工作前将 `Status:` 设为 `claimed` 并保存。
- **解决**：在 `## Answer` 下追加答案，将 `Status:` 设为 `resolved`，再向 `map.md` 的 Decisions-so-far 追加上下文指针（概要和链接）。
