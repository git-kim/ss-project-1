MAP = {
    "anmlInctCdNm": "동물곤충원인",
    "cptcSeCdNm": "관할구분",
    "egrcSidoCdNm": "긴급구조시",
    "egrcSiggCdNm": "긴급구조구",
    "emtpQlcClCd1Nm": "구급대원1_자격",
    "emtpQlcClCd2Nm": "구급대원2_자격",
    "emtpQlcClCd3Nm": "운전요원_자격",
    "frnrAt": "내외국인",
    "frnrAt": "외국인여부",
    "gutHh": "출동시",
    "gutYm": "출동년월",
    "ptntAge": "환자연령",
    "ptntOccrTyCd1Nm": "질병외_교통사고",
    "ptntOccrTyCd2Nm": "질병외_사고부상",
    "ptntOccrTyCd3Nm": "질병외_비외상성질환",
    "ptntSdtSeCdNm": "환자성별",
    "ptntTyCdNm": "환자유형",
    "rcptPathCdNm": "접수경로",
    "rlifAcdAsmCdNm": "구급사고유형",
    "rlifOccrTyCdNm": "발생유형",
    "rsacGutFsttOgidNm": "출동소방서",
    "ruptOccrPlcCdNm": "구급사고발생장소",
    "ruptSptmCdNm": "환자증상",
    "sidoHqOgidNm": "시도본부",
    "sptMvmnDtc": "현장과의거리",
    "stmtHh": "신고시",
    "stmtYm": "신고년월",
    "wmhtDamgCdNm": "온열손상"
}

def interpret_column(column_name: str) -> str | None:
    return MAP.get(column_name, None)
