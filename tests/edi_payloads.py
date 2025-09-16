"""Reusable EDI payloads covering common healthcare X12 transactions."""

from __future__ import annotations

from typing import Iterable

SEGMENT_DELIMITER = "~"
LINE_BREAK = "\n"


def join_segments(segments: Iterable[str]) -> str:
    """Build an X12 payload with standard delimiters."""
    return f"{SEGMENT_DELIMITER}{LINE_BREAK}".join(segment.rstrip(SEGMENT_DELIMITER) for segment in segments) + SEGMENT_DELIMITER


SAMPLE_837_PROFESSIONAL = join_segments(
    [
        "ISA*00*          *00*          *ZZ*CLINIC837      *ZZ*RECEIVER837   *20240301*1015*^*00501*000000001*0*T*:",
        "GS*HC*CLINIC837*RECEIVER837*20240301*1015*1*X*005010X222A1",
        "ST*837*1001*005010X222A1",
        "BHT*0019*00*20240315*1015*CH",
        "NM1*41*2*CLINIC 837*****46*1234567890",
        "PER*IC*CLAIMS CONTACT*TE*5551234567",
        "NM1*QC*1*DOE*JANE*M***MI*W123456789",
        "DMG*D8*19801025*F",
        "CLM*ABC123456*250.00***11:B:1*Y*A*Y*I",
        "HI*ABK*A1234*ABF*B5678",
        "SV2*HC:99213*1*125.50*125.50",
        "DTM*472*20240315",
        "SV2*HC:87070*2*62.50*125.00",
        "SE*12*1001",
        "GE*1*1",
        "IEA*1*000000001",
    ]
)

SAMPLE_837_INSTITUTIONAL = join_segments(
    [
        "ISA*00*          *00*          *ZZ*HOSP837I      *ZZ*RECEIVER837I  *20240301*1415*^*00501*000000011*0*T*:",
        "GS*HC*HOSP837I*RECEIVER837I*20240301*1415*2*X*005010X223A2",
        "ST*837*1002*005010X223A2",
        "BHT*0019*00*03152024*0900*CH",
        "NM1*41*2*GENERAL HOSPITAL*****46*5558889999",
        "CLM*ZYX987654*$1,234.56***11:B:1*Y*A*Y*I",
        "HI*ABK*C1234*ABF*D5678*APR*E1111",
        "SV2*HC:27447*3*100.00*300.00",
        "SE*7*1002",
        "GE*1*2",
        "IEA*1*000000011",
    ]
)

SAMPLE_835_REMITTANCE = join_segments(
    [
        "ISA*00*          *00*          *ZZ*PAYER835      *ZZ*RECEIVER835   *20240402*0815*^*00501*000000021*1*T*:",
        "GS*HP*PAYER835*RECEIVER835*20240402*0815*1*X*005010X221A1",
        "ST*835*2001*005010X221A1",
        "BPR*I*1500.00*C*CHK*123456789*DA*987654321*20240402",
        "TRN*1*12345*1512345678*9876543210",
        "DTM*405*20240401",
        "NM1*41*2*MAJOR PAYER*****46*999888777",
        "NM1*85*2*TRUSTED PROVIDER*****XX*1234567893",
        "CLP*123456789*1*1750.00*1500.00*250.00*MC*12345*11*1",
        "CAS*CO*45*250.00",
        "SE*9*2001",
        "GE*1*1",
        "IEA*1*000000021",
    ]
)

SAMPLE_834_ENROLLMENT = join_segments(
    [
        "ISA*00*          *00*          *ZZ*SPONSOR834    *ZZ*RECEIVER834   *20240403*0900*^*00501*000000031*0*T*:",
        "GS*BE*SPONSOR834*RECEIVER834*20240403*0900*1*X*005010X220A1",
        "ST*834*3001*005010X220A1",
        "BGN*00*20240402*0900*00*2*RX",
        "NM1*38*2*BIG EMPLOYER*****46*EMP001",
        "INS*Y*MEM001*JOHN*DOE*19800101*M*20240101",
        "REF*0F*MEM001",
        "INS*Y*DEP001*JANE*DOE*20080215*F*20240201",
        "REF*0F*DEP001",
        "SE*8*3001",
        "GE*1*1",
        "IEA*1*000000031",
    ]
)

SAMPLE_270_ELIGIBILITY = join_segments(
    [
        "ISA*00*          *00*          *ZZ*REQ270        *ZZ*RESP270       *20240404*1000*^*00501*000000041*0*T*:",
        "GS*HS*REQ270*RESP270*20240404*1000*1*X*005010X279A1",
        "ST*270*4001*005010X279A1",
        "BHT*0022*13*270123*20240404*1000",
        "HL*1**20*1",
        "NM1*PR*2*PAYER*****PI*12345",
        "SE*5*4001",
        "GE*1*1",
        "IEA*1*000000041",
    ]
)

SAMPLE_271_ELIGIBILITY_RESPONSE = join_segments(
    [
        "ISA*00*          *00*          *ZZ*RESP271       *ZZ*REQ271        *20240405*1115*^*00501*000000051*0*T*:",
        "GS*HS*RESP271*REQ271*20240405*1115*1*X*005010X279A1",
        "ST*271*5001*005010X279A1",
        "BHT*0022*11*271321*20240405*1115",
        "HL*1**20*1",
        "NM1*IL*1*DOE*JANE****MI*987654321",
        "SE*5*5001",
        "GE*1*1",
        "IEA*1*000000051",
    ]
)
