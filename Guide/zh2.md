unity写的音乐游戏音击解密和运行
图就不配了，tg搜索可以下载到解密好的游戏整合版本，需要控制器或者开源控制器应用（键鼠手机版本都有）连接游玩。

一些说明：Unity跨平台游戏，为了防止代码被轻易逆向分析，常常会对Assembly-CSharp.dll等关键 Managed DLL进行加密，这些DLL不会直接以标准的PE/COFF (Windows) 或ELF(Linux/Android) 格式存储在文件中，而通常会以加密的形式打包在游戏资源或二进制文件中。当游戏启动时，Mono 运行时（由libmono.so提供）会负责加载和解密这些 DLL。

核心原因：当Unity的Mono运行时（本游戏非IL2CPP运行时，是libmono.so，是Mono后端）尝试加载这个MetaData签名被破坏的Assembly-CSharp.dll时，它会发现：
 * 这个 DLL 的 PE 头虽然存在，但其 .NET Metadata 部分的标志（即 BSJB 签名）不正确。
 * 这对于运行时来说是一个致命错误。它无法识别这个文件是一个有效的 .NET 程序集，因此无法正确解析其中的类型、方法、字段等信息。
 * 结果就是：Unity 引擎在加载核心 DLL 的过程中遭遇了“内部文件格式错误”或“程序集损坏”的判断，从而导致游戏无法正常初始化，表现为闪退。它根本无法执行 DLL 中的任何代码。

音击游戏运行在英特尔x86技嘉b250主板上，游戏使用x64指令集，系统是win10 iot。世嘉在游戏街机电脑上使用了自己定制的io控制外设板，并将定制的验证序列写入了板载的单片机上，只有验证成功才能运行游戏。所以游戏本体不经过兼容性修复，通用x86电脑无法运行游戏。
运行这个游戏有两种途径：修复游戏软件的启动方式和使用定制硬件进行加密游戏的运行。
开源定制板运行方案由于很难拿到定制外设板进行分析，重新实现并制作来启动，需要等待有愿意免费提供定制外设板分析资料的有缘人。目前来看公开的资料非常零散，收集的时间成本很高。
所以本分析使用的是修复游戏软件的启动方式。

一些知识：
一、Unity引擎内部的.NET程序集校验
当dump出来Assembly-CSharp.dll但未修复其.NET Metadata 签名（即后续得到的BSJB签名）时，虽然文件内容可能已经被解密，但它的“外壳”——也就是 PE 文件头中的元数据部分，对于标准的 .NET 加载器来说是无效的。

二、unity游戏启动器虽基本通用但引擎自带检查功能
unity引擎跟其他游戏引擎比较像，非定制启动器可以进行通用启动，也就是说可以拿两个同引擎的启动exe相互替换也能正常启动。
UnityLoader.exe或者Unity引擎本身（无论是什么启动器）在启动游戏时，会尝试加载和初始化这些 .NET 程序集（DLL）。这个加载过程会包含对DLL完整性和有效性的检查。

一些面对新手的补充:核心逻辑通常封装在 Assembly-CSharp.dll 文件中。但很多时候，我们发现直接用 .NET 工具打不开这个 DLL，或者它被加密了。需要解密并修复它。准备好以下工具:IDA Pro，WinHex，LoadPE，.NET Reflector (或 dnSpy 等): 用于验证解密修复后的 DLL 是否可正常打开。
 * 游戏本体: 当然，你得有《音击》游戏本体。这里提一嘴，某些渠道（比如在 Telegram 搜索）可能已经有解密好的整合版本，但如果你想自己动手理解原理，或者处理更特殊的版本，下面的方法是你的不二选择。别忘了准备好控制器，或使用开源控制器应用，无论是键鼠还是手机版本都能连接游玩。
第一步：运行时拦截解密 (libmono.so 动态修改)
这一步的目标是在游戏运行过程中，捕获 Assembly-CSharp.dll 被解密后的内存数据。
1. 修改 libmono.so，制造“暂停点”：
首先，找到游戏目录下的 libmono.so 文件。用 WinHex 打开它。
我们要找到 mono_image_open_from_data_with_name_0 这个函数的起始指令，并把它改成一个无限循环。这个函数的地址通常是 003DE1F8。
 * 原始指令 (例如): F0 47 2D E9
 * 修改为无限循环: 将 003DE1F8 处的字节修改为 FE FF FF EA。
这个修改的目的是让游戏在尝试加载 Assembly-CSharp.dll 时，卡在这个函数入口，给我们足够的窗口时间来附加 IDA Pro。
2. 在 IDA Pro 中设置断点：
打开 IDA Pro，加载修改过的 libmono.so。
你需要找到在 .bss 段中的一个特定地址，这里是 761F1FC。在这个地址上，有一条指令是 LDR R4, [SP, #0x24]。在这里设置一个断点。
3. 运行游戏并附加 IDA Pro：
现在，启动《音击》游戏。由于你修改了 libmono.so，游戏应该会在加载 DLL 的地方卡住。
打开 IDA Pro，选择“Debugger” -> “Attach to process...”，然后选择正在运行的《音击》进程并附加。
4. 动态调试与数据捕获：
 * 附加成功后，在 IDA Pro 中按 F9 运行程序。
 * 打开 IDA 的“断点列表”（Debugger -> Breakpoints）。
 * 双击列表中的断点，这将快速跳转到 mono_image_open_from_data_with_name_0 函数的入口处（准确地说，是你设置的无限循环处，地址 003DE1F8）。
 * 关键操作：
   * 此时，程序停在了你设置的无限循环点。现在，在 IDA Pro 中修改内存，把 003DE1F8 处的指令还原回原始的字节序列：FE FF FF EA 改回 F0 47 2D E9。这样做是为了让函数能够继续执行。
   * 请注意 mono_image_open_from_data_with_name_0 的第一个参数 r0。它指向了即将被处理的数据缓冲区。第二个参数 r1 代表了这个缓冲区的大小。
   * 在当前暂停点，检查 r0 所指向的内存内容。如果它以 MZ 开头（这是 Windows PE 可执行文件的标志），那么这次的 buffer 可能不是你关心的 Assembly-CSharp.dll，或者它已经处于解密状态了。
   * 如果 r0 指向的不是 MZ 开头的数据，那么它很有可能就是我们等待解密的 Assembly-CSharp.dll 的加密数据。此时，再按一下 F9。
   * 程序会在你之前设置的 .bss:761F1FC 断点处停下。恭喜你，此时 Assembly-CSharp.dll 的解密过程已经完成！ r0 指向的内存就是解密后的 DLL 数据。
   * 使用 IDA Pro 的脚本功能（通常是 Python 脚本），将 r0 指向的 buffer 内容，以 r1 为大小，dump 出来保存为一个新的文件，比如命名为 Assembly-CSharp.dll.decrypted。
 * 收尾工作：
   * dump 完数据后，你可能需要反复多次按 F9 运行，以确保所有相关的 DLL 加载流程都已完成。
   * 为了后续方便，你可能还需要在 libmono.so 中将 mono_image_open_from_data_with_name_0 函数内部的解密循环函数通过 NOP 或修改跳转指令的方式“跳过”。这样，下次它就不会再对这个 DLL 进行重复解密了。
第二步：修复 Assembly-CSharp.dll (.NET Metadata 签名修复)
虽然你已经 dump 出了数据，但它可能还无法直接被 .NET 反编译工具识别。这是因为 .NET 程序集的元数据签名可能被破坏或清除了。

正常说明:
1. 定位元数据信息：
用 LoadPE 打开你刚刚 dump 出来的 Assembly-CSharp.dll.decrypted 文件。
 * 查看 PE 头部的 IMAGE_DATA_DIRECTORY 部分，找到 .NET Metadata 所在的条目。
 * 记录下 MetaData 的 RVA (相对虚拟地址) 和 大小。例如，你可能会看到 MetaData 0x001A7558 0x001C752C，这表示 MetaData 的 RVA 是 0x001A7558，大小是 0x001C752C。
2. 计算文件偏移：
在 LoadPE 中，切换到“区段”视图。找到 MetaData RVA (0x001A7558) 所处的区段。通常，它会在 .text 段中。
 * 记录下该区段的 VirtualAddress (虚拟地址) 和 PointerToRawData (文件中的原始数据偏移)。
 * 根据这些信息，计算 MetaData 在文件中的实际偏移：
   文件偏移 = MetaData RVA - 所在区段的 VirtualAddress + 所在区段的 PointerToRawData
 * 例如，如果 .text 段信息是 00002000 (VirtualAddress) 和 00000200 (PointerToRawData)，那么计算结果就是：
   0x001A7558 - 0x00002000 + 0x00000200 = 0x1A5758
3. 用 WinHex 修复签名：
用 WinHex 打开你 dump 出来的 Assembly-CSharp.dll.decrypted 文件。
 * 跳转到刚刚计算出的文件偏移 0x1A5758 处。
 * 你会发现这里可能不是 BSJB。请将这 4 个字节修改为标准的 .NET 元数据签名：42 53 4A 42 (即 ASCII 字符 "BSJB")。
 * 保存文件。
4. 验证修复成果：
现在，尝试用 .NET Reflector (或 dnSpy) 打开你修改后的 Assembly-CSharp.dll.decrypted 文件。如果一切顺利，它应该能够被正常识别并加载和查看代码。

补充新手说明:
工作原理简析：
 * 第一步：解密
   * Unity 游戏为了保护代码，会将核心 DLL（比如 Assembly-CSharp.dll）进行加密，并将其打包在游戏资源中。
   * 当游戏运行到需要加载这些 DLL 时，libmono.so 中的 mono_image_open_from_data_with_name_0 函数会被调用，它负责将加密数据解密到内存中。
   * 我们通过修改 libmono.so 和设置断点，强行介入这个过程，在数据被解密到内存中后，但在 Mono 运行时进一步处理它之前，将其 dump 出来。
 * 第二步：修复元数据签名
   * 即使解密了 DLL 的内容，但有时为了防逆向，文件的 .NET Metadata 结构中的起始签名 (lSignature) 会被故意破坏或清空。
   * 这个签名 (BSJB) 对于 .NET 工具识别一个文件是否为有效的 .NET 程序集至关重要。
   * 通过 LoadPE 找到元数据在文件中的准确位置，然后用 WinHex 手动将其修复为正确的 BSJB 签名，欺骗 .NET 工具，使其能够正确解析和反编译这个 DLL。
Assembly-CShar

总之要对 libmono.so 的运行时内存修改以及对 .dll 文件本身的二进制修复。这整个过程是为了让加密的 Assembly-CSharp.dll 能够被像 .NET Reflector 这样的工具正确识别和加载。
第一部分：解密 Assembly-CSharp.dll (运行时解密)
这一部分主要关注的是在游戏运行时，通过拦截 libmono.so 中的 mono_image_open_from_data_with_name_0 函数来获取解密后的 Assembly-CSharp.dll 数据。
原理：
 * 加密方式：Unity 游戏，特别是移动平台上的游戏，为了防止代码被轻易逆向分析，常常会对 Assembly-CSharp.dll 等关键 Managed DLL 进行加密。这些 DLL 不会直接以标准的 PE/COFF (Windows) 或 ELF (Linux/Android) 格式存储在文件中，而通常会以加密的形式打包在游戏资源或二进制文件中。当游戏启动时，Mono 运行时（由 libmono.so 提供）会负责加载和解密这些 DLL。
 * mono_image_open_from_data_with_name_0 函数的作用：
   * 这个函数是 Mono 运行时加载 DLL 的核心函数之一。它通常接收一个指向内存中加密或原始 DLL 数据的 buffer (通过 r0 参数传递) 和 buffer 的大小 (通过 r1 参数传递)。
   * 在加载加密 DLL 的过程中，游戏通常会在调用 mono_image_open_from_data_with_name_0 之前，或在函数内部的某个点执行解密操作。
 * 无限循环和断点的作用（运行时拦截）：
   * 第一次无限循环 (WinHex 修改 003DE1F8): 将 mono_image_open_from_data_with_name_0 的第一条指令改成无限循环，目的是为了在游戏启动时，当尝试加载 Assembly-CSharp.dll 时，强制程序进入一个等待状态。这样你就有时间附加 IDA Pro 到游戏进程。
   * IDA Pro 附加和 F9 运行：附加后，你可以在 IDA 中控制游戏的执行流。
   * 第二个断点 (.bss:761F1FC 的 LDR R4, [SP, #0x24]): 这个断点是一个策略性的位置。当程序在第一次断点（在 mono_image_open_from_data_with_name_0 的第二条指令处）暂停时，你检查 r0 指向的数据。
     * 如果数据是 MZ 开头（Windows PE 文件的标志），说明它已经是解密后的标准 PE 文件头，这通常意味着这个 buffer 可能是另一个已经解密的 DLL 或者不是你当前关心的目标。
     * 如果不是 MZ 开头，说明这很可能是加密的 Assembly-CSharp.dll 数据，并且程序将继续执行解密逻辑。
     * 当你再次按 F9 并在第二个断点处断下时，根据你的经验，此时 Assembly-CSharp.dll 的解密过程已经完成，r0 指向的 buffer 中应该存放着解密后的数据。
   * 还原无限循环 (IDA 中修改内存)：在第二个断点处，你需要将之前设置的无限循环还原，以允许 mono_image_open_from_data_with_name_0 函数正常执行完成。这是因为你只需要获取解密后的数据，而不需要阻止其后续的 Mono 内部处理。
   * 反复多次 F9 运行：这可能是为了确保所有的 Assembly-CSharp.dll 相关的部分都被正确处理和解密，或者因为 mono_image_open_from_data_with_name_0 可能会被多次调用来处理不同的数据块。
   * 用 IDA 脚本 Dump 数据：一旦确认 r0 指向的是解密后的数据，就可以使用 IDA Pro 的内置脚本或 Python 脚本将 r0 指向的内存区域（大小由 r1 决定）保存到文件中。这就是你获取到解密后的 Assembly-CSharp.dll 文件的方式。
 * 跳过解密循环函数：这指的是在 mono_image_open_from_data_with_name_0 函数内部，可能有一个专门的子函数负责实际的解密逻辑。为了避免libmono.so 在加载其他 Mono Image 时再次执行同样的解密逻辑（或者防止对同一个 buffer 进行不必要的重复解密），有时需要对 libmono.so 进行进一步的修改，跳过或 NOP 掉这段解密循环的代码。这样，你未来在加载这个 libmono.so 时，它就不会再对 Assembly-CSharp.dll 进行解密，因为它期望你已经提供了“干净”的 DLL。
第二部分：修复 .dll 文件 (元数据签名修复)
这一部分主要解决的是虽然 .dll 文件已经被解密并 dump 下来，但它可能仍然无法被 .NET Reflector 等工具识别的问题。
原理：
 * IMAGE_DATA_DIRECTORY MetaData 结构和 lSignature：
   * PE (Portable Executable) 文件格式是 Windows 可执行文件和 DLL 的标准格式。它包含一个 IMAGE_OPTIONAL_HEADER 结构，其中有一个 DataDirectory 数组。
   * IMAGE_DATA_DIRECTORY 数组的第 14 个条目（索引为 14）通常指向 .NET Metadata 目录（在 .NET 程序集特有的 PE 头部）。
   * .NET Metadata 目录的起始处有一个签名 (lSignature)。对于有效的 .NET 程序集，这个签名必须是特定的值，通常是 0x42534A42 (即 ASCII 字符 "BSJB")。
   * 如果这个签名不正确，像 .NET Reflector 这样的工具就会认为这不是一个有效的 .NET 程序集文件，从而无法打开和分析它。
 * 为什么会不正确？：
   * 部分解密：虽然你成功 dump 出了数据，但可能只是 DLL 的主体部分被解密了，而其 PE 头部（特别是 Metadata 部分的签名）在原始加密过程中可能被篡改或并未包含在正常的解密流程中。
   * 防逆向措施：游戏开发者可能会故意修改或清空这个签名，作为一种简单的反逆向工程手段，使得即使解密了文件，也无法直接用现有工具打开。
 * 修复过程：
   * LoadPE 定位 MetaData RVA 和大小：LoadPE 是一个 PE 文件分析工具。通过它，你可以查看 PE 文件的内部结构，包括 DataDirectory 中的各个条目，从而获取 MetaData 结构的相对虚拟地址（RVA）和大小。
   * 计算文件偏移：PE 文件中的 RVA 是相对于其加载到内存中的基地址而言的。为了在文件中定位这个 RVA，你需要根据文件的区段信息进行转换：
     * 文件偏移 = RVA - 所在区段的虚拟地址 (VirtualAddress) + 所在区段的文件偏移 (PointerToRawData)
     * 例如，你的计算 001A7558 - 00002000 + 00000200 = 1A5758 就是将内存中的 RVA 转换为文件中的物理偏移。
   * WinHex 修改 BSJB：使用 WinHex (一个十六进制编辑器)，跳转到计算出的文件偏移 1A5758 处，将该地址处的 4 个字节修改为 0x42534A42 (即 ASCII "BSJB")。
   * IDA 识别：当你修改并保存文件后，再次尝试用 IDA Pro 打开，它现在应该能够正确识别出这是一个 .NET 程序集，并且会显示出其 CIL (Common Intermediate Language) 代码，而不是原始的二进制数据。同样，.NET Reflector 也应该能够打开它了。
总结原理：
整个过程是一个典型的逆向工程流程，涉及到动态分析和静态修复：
 * 动态分析：利用 IDA Pro 附加到游戏进程，通过修改 libmono.so 的指令和设置断点，拦截 Assembly-CSharp.dll 在内存中被解密后的数据流，并将其 dump 出来。这一步解决了数据内容加密的问题。
 * 静态修复：针对 dump 出来的 .dll 文件，通过分析其 PE 结构，发现其 .NET Metadata 签名的损坏或缺失，并使用十六进制编辑器直接修改文件，将其修复为标准的 BSJB 签名，解决了文件格式识别问题，使得通用的 .NET 工具能够正确解析文件。


前置说明，原理，用到的知识和过程的说明就不说了，在开源项目里会补充上或者等待有pr的补充
dump出来的vhd解包部分先不说了
（一般很少很少冒险从游戏店里，在店员和监控的不断监视下d出来的，不太可能，相当于从没发售的游戏公司的开发机里拿游戏本体，被抓按里本法律要坐几年牢，非常的不公平。致敬，每一个，传奇leaker。一般都是花钱从不明渠道买，这个东西没办法跟批量通贩游戏的售价来比，价格从2000到上wrmb不等。）

游戏用unity写的。其他两个dll和exe修复在本开源项目的舞萌中二游戏分析那里进行通用处理，然后三个游戏的签名都不一样，所以分开展示。

用ida pro打开libmono.so
找到mono_image_open_from_data_with_name
顺藤摸瓜找到mono_image_open_from_data_with_name_0
把mono_image_open_from_data_with_name_0第一条指令
改成无限循环（用winhex）：003DE1F8  F0 47 2D E9  --> FEFFFFEA

然后在.bss段中
找到地址为761F1FC的指令：LDR R4, [SP, #0x24]
下断点，然后运行游戏，挂在目标
并按 F9 运行之后打开断点列表，双击断点
这样就能快速来到函数mono_image_open_from_data_with_name_0处
 
来到mono_image_open_from_data_with_name_0（003DE1F8 ）第二条指令，无限循环处，在ida中修改内存把mono_image_open_from_data_with_name_0
第一条指令的无限循环 还原回去：003DE1F8  FE FF FF EA    -->  F0 47 2D E9
之后，反复多次的按F9运行
mono_image_open_from_data_with_name_0 的第一个参数的 r0，代表着目标 buffer，第二个参数 r1 代表着 buffer 的大小

在第一次断点触发暂停后
程序停在了 mono_image_open_from_data_with_name_0的第二条指令，跟r0所指向的内存
如果是MZ开头的，那么就不用关心本次解密，如果不是MZ开头的，再按一下F9，程序会在第二个断点处断下，此时解密完成
用ida脚本（基本都用python写）dump下来，之后需要把libmomo.so的mono_image_open_from_data_with_name_0 这个函数的中的解密循环函数给跳过。

用.net reflector（dnspy也可以）打开.so文件
可以看到name行其实就是IMAGE_DATA_DIRECTORY MetaData; 中的第一个字段lSignature结构不是'BSJB'造成的
相关知识如下：http://www.52pojie.cn/thread-299156-1-1.html

快速定位：把目标 dll 拖入 LoadPE，记录下MetaData的数值：
MetaData 0x001A7558 0x001C752C
0x001A7558是 MetaData 在内存中的 RVA，0x001C752C是MetaData结构的大小。

点击“区段”记录下pe的区段信息：
.text  00002000  0036CA84  00000200  0036CC00
发现MetaData在内存中的 RVA（0x001A7558）落在.text段
根据.text段信息计算，MetaData 数据在文件中的偏移：001A7558-00002000+00000200=1A5758。用winhex打开目标dll来到1A5758偏移处，修改数据为：'BSJB'。保存后，IDA 已经识别。