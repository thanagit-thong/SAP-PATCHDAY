from src.collectors.patchday import (
    monthly_bulletin_url,
    yearly_archive_url,
    extract_month_section,
)


def test_monthly_url():
    url = monthly_bulletin_url(2026, 9)

    assert url.endswith("/september-2026.html")


def test_yearly_archive_url():
    url = yearly_archive_url(2025)

    assert url.endswith("/bulletin-2025.html")


def test_extract_month_section():
    html = """
    <html>
      <body>

        <h2>SAP Security Patch Day - January 2025</h2>
        <p>January content</p>
        <table>
          <tr>
            <td>3537476</td>
            <td>Test January Note</td>
          </tr>
        </table>

        <h2>SAP Security Patch Day - February 2025</h2>
        <p>February content</p>

      </body>
    </html>
    """

    result = extract_month_section(
        html,
        2025,
        1,
    )

    assert "3537476" in result
    assert "January content" in result
    assert "February content" not in result
