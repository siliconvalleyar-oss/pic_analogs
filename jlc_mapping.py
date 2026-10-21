#!/usr/bin/env python3
"""
Mapeo de componentes a JLCPCB part numbers.
"""

JLC_MAPPING = {
    # Resistencias 0603
    "Device:R_US|10K": "C25804",
    "Device:R_US|10k": "C25804",
    "Device:R_US|2k2": "C25808",
    "Device:R_US|100": "C25797",
    "Device:R_US|27": "C25790",
    "Device:R_US|4K7": "C25802",
    "Device:R_US|1K": "C25800",
    
    "Device:R_Small_US|100": "C25797",
    "Device:R_Small_US|10k": "C25804",
    "Device:R_Small_US|1k": "C25800",
    
    "Device:R|100": "C25797",
    "Device:R|10K": "C25804",
    "Device:R|1K5": "C25801",
    "Device:R|27": "C25790",
    "Device:R|4K7": "C25802",
    
    # Capacitores 0603
    "Device:C|100n": "C115188",
    "Device:C|100nf": "C115188",
    "Device:C|10n": "C115184",
    "Device:C|15p": "C115174",
    "Device:C|15pf": "C115174",
    "Device:C|33nf": "C115182",
    
    # MCU
    "MCU_Microchip_PIC18:PIC18F4550-IPT|PIC18F4550-IPT": "C420477",
    
    # FT232
    "Interface_USB:FT232BM|FT232BM": "C2882209",
    
    # Regulador LM1117-3.3
    "Regulator_Linear:LM1117DT-3.3|LM1117DT-3.3": "C17654",
    
    # MRF24J40
    "RF_ZigBee:MRF24J40MA|MRF24J40MA": "C423125",
    
    # EEPROM 25LCxxx
    "Memory_EEPROM:25LCxxx|25LCxxx": "C173228",
    
    # MOSFET FDN306P (P-channel)
    "FDN306P:FDN306P|FDN306P": "C436776",
    
    # 2N7002 (N-channel)
    "Transistor_FET:2N7002|2N7002": "C436786",
    
    # 1N4148W
    "Diode:1N4148W|1N4148W": "C423142",
    
    # SS2040 (Schottky)
    "Device:D_Shockley|ss2040": "C423158",
    
    # LEDs
    "Device:LED|LED": "C423170",
    "Device:LED|LED_RD0": "C423170",
    "Device:LED|LED_RD1": "C423170",
    "Device:LED|LED_RD2": "C423170",
    "Device:LED|LED_RD3": "C423170",
    "Device:LED_Small|DBG": "C423170",
    "Device:LED_Small|RX": "C423170",
    
    # Ferrite beads
    "Device:FerriteBead|10M": "C173206",
    
    # Inductors
    "Device:L|100mh": "C173214",
    "Device:L|L": "C173214",
    
    # Crystals
    "Device:Crystal|6Mhz": "C423192",
    "Device:Crystal_GND24_Small|Crystal_GND24_Small": "C423192",
    
    # Switches
    "Switch:SW_Push_Dual_x2|mclr": "C423200",
    "Switch:SW_Push_Dual_x2|ra4": "C423200",
    "Switch:SW_Push_Dual_x2|ra5": "C423200",
    "Switch:SW_Push_Dual_x2|rb4": "C423200",
}

EXCLUDED_FROM_JLC = {
    "Connector:Conn_01x01_Pin", "Connector:Conn_01x04_Pin", 
    "Connector:Conn_01x06_Pin", "Connector:Conn_01x07_Pin",
    "Connector:Conn_01x14_Pin", "Connector:Conn_Coaxial",
    "Connector:F32R-1A7H1-11024", "Connector:Micro_SD_Card",
    "Connector:Raspberry_Pi_zero_2w", "Connector:USB_A",
    "Connector:USB_B_Mini", "Connector_Generic:Conn_01x02",
    "Connector_Generic:Conn_01x06",
    "Jumper:Jumper_2_Open", "Jumper:SolderJumper_2_Open",
    "Simulation_SPICE:PMOS",
    "power:+3.3V", "power:+3V3", "power:+5F", "power:+5V", "power:GND"
}

def get_jlc_part(lib_id, value):
    key = f"{lib_id}|{value}"
    if key in JLC_MAPPING:
        return JLC_MAPPING[key]
    if lib_id in EXCLUDED_FROM_JLC:
        return None
    return None

if __name__ == "__main__":
    import json
    print(json.dumps(JLC_MAPPING, indent=2))
