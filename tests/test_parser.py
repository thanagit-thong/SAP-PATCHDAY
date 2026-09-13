from src.parsers.patchday_parser import parse_bulletin


def test_parse_simple_row():
    html = """
    <table>
      <tr><th>Note#</th><th>Title</th><th>Priority</th><th>CVSS</th></tr>
      <tr>
        <td>3747649</td>
        <td>[CVE-2026-44756] Memory Corruption vulnerability in SAP Product
            Version(s) - KERNEL 7.93</td>
        <td>Critical</td>
        <td>10.0</td>
      </tr>
    </table>
    """
    notes, summary = parse_bulletin(html)

    assert len(notes) == 1
    assert notes[0]["note_number"] == "3747649"
    assert notes[0]["cve"] == ["CVE-2026-44756"]
    assert notes[0]["priority"] == "Critical"
    assert notes[0]["cvss"] == 10.0
