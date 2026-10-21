#!/usr/bin/env python3
"""
Agrega mapeo para Device:R_US con valor "R_US" (usar 10k por defecto)
"""

import re

JLC_MAPPING = {
    "Device:R_US|10K": "C25804",
    "Device:R_US|10k": "C25804",
    "Device:R_US|2k2": "C25808",
    "Device:R_US|100": "C25797",
    "Device:R_US|27": "C25790",
    "Device:R_US|4K7": "C25802",
    "Device:R_US|1K": "C25800",
    "Device:R_US|R_US": "C25804",   # AGREGADO: default 10k para R_US sin valor
    "Device:R_Small_US|100": "C25797",
    "Device:R_Small_US|10k": "C25804",
    "Device:R_Small_US|1k": "C25800",
    "Device:R|100": "C25797",
    "Device:R|10K": "C25804",
    "Device:R|1K5": "C25801",
    "Device:R|27": "C25790",
    "Device:R|4K7": "C25802",
    "Device:C|100n": "CC0603KRX7R9BB104",
    "Device:C|100nf": "CC0603KRX7R9BB104",
    "Device:C|10n": "C115184",
    "Device:C|15p": "C115174",
    "Device:C|15pf": "C115174",
    "Device:C|33nf": "C115182",
    "MCU_Microchip_PIC18:PIC18F4550-IPT|PIC18F4550-IPT": "C420477",
    "Interface_USB:FT232BM|FT232BM": "C2882209",
    "Regulator_Linear:LM1117DT-3.3|LM1117DT-3.3": "C17654",
    "RF_ZigBee:MRF24J40MA|MRF24J40MA": "C423125",
    "Memory_EEPROM:25LCxxx|25LCxxx": "C173228",
    "FDN306P:FDN306P|FDN306P": "C436776",
    "Transistor_FET:2N7002|2N7002": "C436786",
    "Diode:1N4148W|1N4148W": "C423142",
    "Device:D_Shockley|ss2040": "C423158",
    "Device:LED|LED": "C423170",
    "Device:LED|LED_RD0": "C423170",
    "Device:LED|LED_RD1": "C423170",
    "Device:LED|LED_RD2": "C423170",
    "Device:LED|LED_RD3": "C423170",
    "Device:LED_Small|DBG": "C423170",
    "Device:LED_Small|RX": "C423170",
    "Device:FerriteBead|10M": "C173206",
    "Device:L|100mh": "C173214",
    "Device:L|L": "C173214",
    "Device:Crystal|6Mhz": "C423192",
    "Device:Crystal_GND24_Small|Crystal_GND24_Small": "C423192",
    "Switch:SW_Push_Dual_x2|mclr": "C423200",
    "Switch:SW_Push_Dual_x2|ra4": "C423200",
    "Switch:SW_Push_Dual_x2|ra5": "C423200",
    "Switch:SW_Push_Dual_x2|rb4": "C423200",
}

EXCLUDED = {
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
    if lib_id in EXCLUDED:
        return None
    return None

def process_symbol_instance(block):
    lib_id_match = re.search(r'\(lib_id\s+"([^"]+)"\)', block)
    if not lib_id_match:
        return block
    lib_id = lib_id_match.group(1)
    
    value_match = re.search(r'\(property\s+"Value"\s+"([^"]+)"', block)
    if not value_match:
        return block
    value = value_match.group(1)
    
    jlc_part = get_jlc_part(lib_id, value)
    if not jlc_part:
        return block
    
    jlc_match = re.search(r'\(property\s+"JLCImport"\s+"([^"]*)"', block)
    if jlc_match and jlc_match.group(1) == jlc_part:
        return block
    
    jlc_property = f'''		(property "JLCImport" "{jlc_part}"
			(at 0 0 0)
			(hide yes)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)'''
    
    if jlc_match:
        old_prop = re.search(r'\(property\s+"JLCImport"\s+"[^"]*".*?\n\s+\)', block, re.DOTALL)
        if old_prop:
            return block[:old_prop.start()] + jlc_property + block[old_prop.end():]
    
    value_prop_match = re.search(r'(\(property\s+"Value"\s+"[^"]+".*?\n\s+\))', block, re.DOTALL)
    if value_prop_match:
        end_pos = value_prop_match.end()
        return block[:end_pos] + '\n' + jlc_property + block[end_pos:]
    
    return block

def parse_and_update(content):
    lines = content.split('\n')
    in_lib_symbols = False
    paren_depth = 0
    output_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        if stripped == '(lib_symbols':
            in_lib_symbols = True
            paren_depth = 1
            output_lines.append(line)
            i += 1
            continue
        
        if in_lib_symbols:
            output_lines.append(line)
            for ch in line:
                if ch == '(':
                    paren_depth += 1
                elif ch == ')':
                    paren_depth -= 1
            if paren_depth == 0:
                in_lib_symbols = False
            i += 1
            continue
        
        if line.startswith('\t(symbol') and not in_lib_symbols:
            symbol_lines = [line]
            paren_depth = 1
            i += 1
            while i < len(lines) and paren_depth > 0:
                symbol_lines.append(lines[i])
                for ch in lines[i]:
                    if ch == '(':
                        paren_depth += 1
                    elif ch == ')':
                        paren_depth -= 1
                i += 1
            
            symbol_block = '\n'.join(symbol_lines)
            updated_block = process_symbol_instance(symbol_block)
            output_lines.append(updated_block)
            continue
        
        output_lines.append(line)
        i += 1
    
    return '\n'.join(output_lines)

def process_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    new_content = parse_and_update(content)
    
    if new_content != content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"Updated: {filepath}")
        return True
    else:
        print(f"No changes: {filepath}")
        return False

if __name__ == "__main__":
    files = [
        'ads1115.kicad_sch', 'buttons_rpi.kicad_sch', 'display_oled.kicad_sch',
        'epaper.kicad_sch', 'ft232.kicad_sch', 'magnetics.kicad_sch', 'mcu_pic.kicad_sch',
        'memory_spi.kicad_sch', 'micro_sd_card.kicad_sch', 'mrf24j40.kicad_sch',
        'oled_mcu.kicad_sch', 'rpi.kicad_sch', 'SWR_meter.kicad_sch'
    ]
    
    for f in files:
        process_file(f)
