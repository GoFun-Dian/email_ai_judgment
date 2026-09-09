import struct
import olefile
import io
import zipfile

def _is_doc_encrypted(payload: bytes) -> bool:
    try:
        ole = olefile.OleFileIO(io.BytesIO(payload))
        if ole.exists("WordDocument"):
            stream = ole.openstream("WordDocument")
            fib_base = stream.read(32)  # FibBase 固定 32 字节
            if len(fib_base) >= 12:
                # wFlags 在 FibBase 偏移 0x0A 处
                w_flags = struct.unpack("<H", fib_base[10:12])[0]
                if w_flags & 0x0100:  # fEncrypted 位
                    ole.close()
                    return True
        ole.close()
    except Exception:
        pass
    return False


def _is_xls_encrypted(payload: bytes) -> bool:
    try:
        ole = olefile.OleFileIO(io.BytesIO(payload))
        stream_name = "Workbook" if ole.exists("Workbook") else "Book" if ole.exists("Book") else None
        if stream_name:
            data = ole.openstream(stream_name).read()
            offset = 0
            # FilePass 通常在文件开头 4KB 内
            while offset < min(len(data), 4096) - 4:
                rec_type = struct.unpack("<H", data[offset:offset+2])[0]
                rec_size = struct.unpack("<H", data[offset+2:offset+4])[0]
                if rec_type == 0x002F:  # FilePass
                    ole.close()
                    return True
                offset += 4 + rec_size
        ole.close()
    except Exception:
        pass
    return False


def _is_ppt_encrypted(payload: bytes) -> bool:
    try:
        ole = olefile.OleFileIO(io.BytesIO(payload))
        # 1. 规范标志：EncryptedSummary 流
        if ole.exists("EncryptedSummary"):
            ole.close()
            return True
        # 2. 兜底：WPS 加密特征（非空用户名但首字节为 0）
        if ole.exists("Current User"):
            data = ole.openstream("Current User").read()
            if len(data) >= 28:
                len_user_name = int.from_bytes(data[20:22], "little")
                if len_user_name > 0 and data[26] == 0 and data[27] == 0:
                    ole.close()
                    return True
        ole.close()
    except Exception:
        pass
    return False


def looks_password_protected(payload: bytes, filename: str) -> bool:
    lower_name = filename.lower()

    print(lower_name)
    # ===== 新版格式：.docx / .pptx / .xlsx（加密后是 OLE2，含 EncryptedPackage）=====
    if lower_name.endswith((".docx", ".pptx", ".xlsx")):
        try:
            ole = olefile.OleFileIO(io.BytesIO(payload))
            if ole.exists("EncryptedPackage"):
                ole.close()
                return True
            ole.close()
        except Exception:
            pass

        if "EncryptedPackage".encode("utf-16-le") in payload[:200000]:
            return True
        return False

    # ===== 旧版格式：.doc =====
    if lower_name.endswith(".doc"):
        return _is_doc_encrypted(payload)

    # ===== 旧版格式：.xls =====
    if lower_name.endswith(".xls"):
        return _is_xls_encrypted(payload)

    # ===== 旧版格式：.ppt =====
    if lower_name.endswith(".ppt"):
        return _is_ppt_encrypted(payload)

    # ===== PDF =====
    if lower_name.endswith(".pdf"):
        return b"/Encrypt" in payload[:200000]

    # ===== ZIP =====
    if lower_name.endswith(".zip"):
        try:
            with zipfile.ZipFile(io.BytesIO(payload)) as zf:
                for info in zf.infolist():
                    if info.flag_bits & 0x01:
                        return True
        except zipfile.BadZipFile:
            pass
        return False

    return False