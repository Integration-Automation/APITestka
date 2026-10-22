# 程式審核：APITestka

## 審核者

工作區程式審核；日期＝2026-10-22；對象＝`APITestka`（`je_api_testka`）；結論＝需修正。

本次是工作樹熱點審核，不是逐行審完。範圍只含套件 `je_api_testka/`。已排除 `test/`、`build/`、`dist/`、`__pycache__/` 與 `docs/` 產生物。

## 審核規範

1. 設計：請求組裝、後端差異與既有命令表是否仍說得通。
2. 可讀性：認知複雜度 ≤ 15、巢狀 ≤ 4、參數 ≤ 7、行 ≤ 120。函式長度本專案上限 50 行，本次通則 80 行，從嚴取 50。
3. 錯誤處理：不使用裸 `except`；`except Exception` 須記錄或再拋出。
4. 死碼：熱點路徑上是否有寫了卻沒有作用的參數或分支。
5. 型別與 docstring：公開請求入口是否有註記；不逐一評分。
6. 安全：請求如何組、TLS `verify`、`shell`、`eval`／`exec`、套件閘門、機密是否寫進 log。
7. 測試：只看熱點旁是否有對應測試檔名稱；本次不執行測試。
8. 效能：日誌是否在每次請求複製完整回應。
9. §6：抽樣對照 PyBreeze 雙重解碼、TestPioneer 結束碼與報告路徑、LoadDensity 子程序契約；不改消費者。
10. 文件同步：`architecture.md` §6、§7 與 `progress.md` 開頭是否與閘門、TLS 敘述一致。

嚴重度：缺陷＝未關閉且應修；建議＝未造成立即損害；備註＝核對後不必改。通過＝無未關閉缺陷；有條件通過＝無立即損害；需修正＝有未關閉缺陷。

## 審核紀錄

#### CR-01 · 缺陷 · 請求內容與斷言結果寫進日誌

- 位置：`je_api_testka/requests_wrapper/request_method.py` 第 81–84、115–120 行；`je_api_testka/httpx_wrapper/httpx_method.py` 第 83–89、105–114 行；`je_api_testka/httpx_wrapper/async_httpx_method.py` 第 75–77、111–114、172–175 行；`je_api_testka/utils/executor/action_executor.py` 第 304 行；`je_api_testka/utils/assert_result/result_check.py` 第 17–18 行；`je_api_testka/utils/xml/xml_file/xml_file.py` 第 50 行。日誌本體在 `je_api_testka/utils/logging/loggin_instance.py` 第 31、61、86–90 行。
- 說明：每次 HTTP 呼叫都以 INFO 把 `kwargs` 整包寫出。動作檔、Python 與 GUI 放在 `kwargs` 裡的標頭、`auth`、`json`、`data`、cookie 會原樣進日誌。`execute_action` 再把整份動作清單寫一次。有斷言時，`check_result` 把整份回應字典寫出，其中含回應標頭、cookie、本文與 `request_body`。XML 解析器在建立時寫出完整 XML 字串。記錄器等級是 DEBUG，檔案處理器與 GUI 佇列都會收到 INFO。檔案在家目錄（或 `APITESTKA_LOG_FILE`），多個行程共用並追加，超過約 10MB 才輪替。
- 依據：安全規範要求不得把機密寫進可留存的輸出。同套件已把 `authorization`、`proxy-authorization`、`cookie`、`set-cookie`、`x-api-key` 視為敏感標頭，但只在選擇性寫入共用請求紀錄時遮罩（`je_api_testka/utils/test_record/contract.py` 第 14、61–62 行），而且仍保留 `request_body`。日誌路徑沒有走這段遮罩。失敗分支的 error 紀錄不含 `kwargs`，不能抵銷前面的 INFO。
- 狀態：未關閉。
- 建議：日誌只留方法、URL、狀態碼、耗時與錯誤種類。寫出前用同一組敏感標頭名稱遮罩，並不要記錄 `auth`、本文、cookie 與 XML 原文。動作清單日誌同樣先遮罩。

#### CR-02 · 缺陷 · 非同步 httpx 的 timeout 沒有交給傳輸層

- 位置：`je_api_testka/httpx_wrapper/async_httpx_method.py` 第 68–92 行；呼叫端含同檔第 118–120、177–180 行，以及 `je_api_testka/graphql_wrapper/graphql_method.py` 第 12、62–67 行、`je_api_testka/gui/request_model.py` 第 98–106 行。
- 說明：`send_httpx_requests_async` 的 `timeout` 只用在 `asyncio.wait_for`。`AsyncClient` 與請求方法都沒有收到這個值。鎖檔中的 httpx 0.28.1 對 client 預設約 5 秒。呼叫端傳更大的逾時（GraphQL 非同步預設 30 秒、GUI 的逾時旋鈕）不會延長傳輸逾時；較短的值仍可能被 `wait_for` 提前取消。同步 `requests` 與同步 httpx 有把 `timeout` 傳進請求。
- 依據：請求組裝應讓公開參數生效。這不是死碼參數，而是參數沒有到達實際發送的那一層，會讓較長逾時的呼叫提早失敗。
- 狀態：未關閉。
- 建議：把同一個 `timeout` 傳給 `AsyncClient` 或該次請求。若仍要 `wait_for`，只把它當作外加取消，不要讓它成為唯一一處看得到逾時的地方。

#### CR-03 · 缺陷 · SOAP 會蓋掉或撞上呼叫端標頭

- 位置：`je_api_testka/requests_wrapper/request_method.py` 第 129–133 行。
- 說明：`soap=True` 時不在這一層發送，而是遞迴呼叫自己，並另做一份只含 `Content-Type: application/soap+xml` 的標頭。`headers` 不是這個函式的具名參數，呼叫端傳入的標頭留在 `kwargs`。遞迴又傳入 `headers=`，於是同時帶標頭時會因重複關鍵字失敗。沒帶標頭時，呼叫端無法再加上 SOAP 動作或其他標頭，因為這份新標頭沒有與原本的合併。`auth`、`json`、`data` 仍會隨 `kwargs` 進去。內層使用預設 `soap=False`，不會無限遞迴；擷取裝飾器也故意略過這層空委派（`request_capture.py` 第 107–108 行）。
- 依據：這是請求如何組的熱點。`soap` 與 `headers` 都是公開路徑上的輸入，組合後應送出合併後的標頭，而不是失敗或丟掉呼叫端標頭。
- 狀態：未關閉。
- 建議：在同一層合併標頭（保留呼叫端的值，缺省時補上 SOAP 的 Content-Type），然後呼叫 `send_requests`，不要再遞迴。

#### CR-04 · 建議 · 套件閘門未設定時仍會載入並發出警告

- 位置：`je_api_testka/utils/package_manager/package_manager_class.py` 第 19–28 行；`je_api_testka/utils/executor/action_executor.py` 第 262–270 行。追蹤項為 `progress.md` 第 9–13 行（#15）。
- 說明：`PackageManager.__init__` 只把設定交給上層，沒有把 `allow_arbitrary_packages` 設為 `False`。文件與 `Executor.set_allow_arbitrary_packages` 的說明寫明：尚未呼叫時，任何已安裝套件會被載入，並發出 `DeprecationWarning`。允許名單與這個開關只在 Python 裡，沒有對應的 `AT_*` 命令，動作檔不能自己打開閘門。`AT_add_package_to_executor` 仍然要經過閘門；預設是「未設定則載入並警告」，不是「完全沒有閘門」。這次沒有把這件事說成遠端任意程式碼已經不受限制。#15 寫明要等警告先隨兩個發行版出去，並先決定只跑動作檔的人要如何允許套件，狀態為 BLOCKED。
- 依據：`architecture.md` §7 與 #15 的敘述和程式一致。安全上這是已知的寬鬆預設，不是已證實的遠端執行缺口。
- 狀態：未關閉，維持建議；與 #15 的時機綁在一起，不在本次升成缺陷。
- 建議：維持文件中的條件。決定動作檔使用者的允許方式之後，再於 `PackageManager.__init__` 把預設改為拒絕名單外套件，並同步三份 README、executor 文件與 §7。

#### CR-05 · 建議 · 非同步路徑沒有接上 GUI 的 TLS 開關

- 位置：`je_api_testka/gui/request_model.py` 第 97–106 行；`je_api_testka/httpx_wrapper/async_httpx_method.py` 第 68–92、97–105 行。對照同步路徑：`httpx_method.py` 第 72、92 行與 `request_method.py` 第 68、87 行。
- 說明：同步 requests 與同步 httpx 的 `verify` 預設 `True`，並傳入資料庫。套件內沒有寫死 `verify=False`。非同步函式沒有 `verify` 參數；GUI 在 `httpx_async` 分支沒有把勾選結果放進 `kwargs`，因此取消「驗證 TLS」不會關閉非同步後端的驗證，實際仍是 httpx 的預設驗證。方向是失敗時偏嚴，不是悄悄關閉 TLS。`allow_redirects` 與 `soap` 也沒有送到非同步後端。動作若在 `kwargs` 自帶 `verify`，非同步請求方法仍會收到，那是呼叫端明示。
- 依據：TLS 規範禁止無說明的 `verify=False`。此處沒有違反那條，但同一個 GUI 開關在三個後端行為不一致，使用者會以為已經關掉驗證。
- 狀態：未關閉，建議。
- 建議：讓非同步入口接受 `verify`，GUI 三個後端都傳入同一個值。預設保持驗證開啟。

沒有第 6 則。抽查沒有另成缺陷的項目寫在「已核對」。

## 方法

閱讀 `architecture.md`（含 §6、§7）、`CLAUDE.md` 的安全與長度、`progress.md` 前 80 行。在 `je_api_testka` 搜尋 `eval(`、`exec(`、`shell=True`、`pickle`、`yaml.load`、`verify=False`、裸 `except`、`subprocess`，以及套件閘門與日誌呼叫。每一則發現都先讀過對應程式，再寫入本檔。沒有改其他檔、沒有執行測試、沒有發 HTTP 請求，也沒有匯入套件去打外部服務。

## 總評

請求主路徑仍是明確的方法表加上 `timeout`，同步兩條路徑預設驗證 TLS，沒有 `shell=True`，也沒有把 `eval`／`exec` 用在動作內容上。套件閘門還在，只是未設定時仍載入並警告。問題集中在三處會直接影響這次熱點的行為：日誌留下標頭與本文、非同步逾時沒有到達 httpx、SOAP 與呼叫端標頭不能一起用。後兩項會讓請求組錯或提早失敗；第一項會把認證材料留在家目錄日誌與 GUI 佇列。因此不是有條件通過。

## 已核對

- `eval(`／`exec(`：沒有用在不受信任的動作上。`gui/main_window.py` 的 `app.exec()` 是 Qt 事件迴圈。`spec/openapi_export.py` 的 `ast.literal_eval` 先用位元組字面值正規表示式限制。
- `shell=True`、`pickle`、`yaml.load`、裸 `except`：套件內沒有相符程式。
- 子程序：`security/cve_check.py` 與 `integrations/load_density_runner.py` 都是參數清單，沒有 shell。前者路徑來自 `shutil.which`，後者是固定的 `python -m je_load_density`。
- TLS：沒有字面 `verify=False`。`connection/connection_options.py` 預設 `verify=True`，只用 `setdefault` 合併。提供者重放在 `contract/verifier.py` 第 108–125 行拒絕非絕對路徑、authority、查詢、片段、過度百分號編碼與 `..`。
- XML：解析走 `defusedxml`（`utils/xml/xml_file/xml_file.py`）。標準庫 ElementTree 用於寫出，檔案內有說明。
- 錯誤吞掉：請求函式的 `except Exception` 有寫日誌並記入 `error_record_list`，與 `cli/cli_common.py` 的 `FailureCount` 設計一致，不是裸 except。
- 機密以外的日誌：GitHub 留言只記 repo 與 PR 編號；Anthropic 後端不接收金鑰，日誌沒有寫出金鑰。
- 繫結：socket 預設 `localhost:9939`；Flask mock 全域實例預設 `localhost:8090`。
- §6 抽樣：`__main__.py` 第 22–28 行仍對 Windows 做兩次 `json.loads`；`FailureCount` 與 `report_path.py` 的 `TEST_PIONEER_ARTIFACT_DIR` 仍在；LoadDensity 仍以無 shell 的子程序與摘要 JSON 判斷。
- 檔案同步：§7 對閘門預設的描述與 CR-04 的程式一致，#15 仍列為未完成。`architecture.md` 開頭「Last verified: 2026-09-22」沒有在這次整份重核。

## 未涵蓋

未執行測試，未送出任何 HTTP 請求。未審 `test/`、`build/`、`dist/`、`__pycache__/`、文件產生物，也未逐行審 GUI 各頁、報告樣板與 mock 路由。`je_action_core` 的 `_check_allowed` 不在本倉庫，閘門行為以本套件包裝、§7 與 #15 為準，沒有在這次匯入後呼叫。舊紀錄與 JSON／HTML 報告仍可能保存標頭與本文；那是報告產物，不是這次認定的 logger，故沒有另開一則。session 方法共用模組層級的 `Session`（`request_method.py` 第 26 行），cookie 會留在行程內，視為既有連線重用，不是本則缺陷。

## 本專案加嚴

函式長度從嚴為 50 行，不是 80。`test_api_method_requests` 具名參數 9 個，超過 7；含簽名字段的本體長於 50 行。三個 HTTP 入口的成功分支結構重複。認知複雜度抽查未見明顯超過 15，巢狀未見超過 4。這些列為加嚴觀察，不另開缺陷，避免把熱點審核變成逐函式長度統計。`except Exception` 在請求路徑有記錄，符合「須記錄或再拋」；沒有因加嚴再記一則。

## 結論

需修正。未關閉缺陷 3 則（CR-01、CR-02、CR-03），建議 2 則（CR-04、CR-05），沒有另計備註則數。CR-04 維持建議：閘門仍在，未設定時載入並警告，不視為遠端任意程式碼已經沒有閘門。
