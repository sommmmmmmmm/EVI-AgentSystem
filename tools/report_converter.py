# -*- coding: utf-8 -*-
"""
보고서 변환 도구 - Markdown을 HTML 및 PDF로 변환
"""

import markdown
from datetime import datetime
from pathlib import Path


class ReportConverter:
    """
    Markdown 보고서를 HTML 및 PDF로 변환
    """

    def __init__(self):
        self.html_template = self._create_html_template()

    def _create_html_template(self) -> str:
        """
        보고서용 HTML 템플릿 생성 - 현대적이고 세련된 디자인
        """
        return """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        :root {{
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --secondary: #8b5cf6;
            --accent: #ec4899;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --info: #3b82f6;
            --dark: #1e293b;
            --gray: #64748b;
            --light-gray: #f1f5f9;
            --border: #e2e8f0;
        }}

        body {{
            font-family: 'Inter', 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
            line-height: 1.7;
            color: var(--dark);
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px 15px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            border-radius: 20px;
            overflow: hidden;
            animation: fadeInUp 0.6s ease-out;
        }}

        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 80px 50px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}

        .header::before {{
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: pulse 15s ease-in-out infinite;
        }}

        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.1); }}
        }}

        .header-content {{
            position: relative;
            z-index: 1;
        }}

        .header h1 {{
            font-size: 3em;
            font-weight: 900;
            margin-bottom: 20px;
            letter-spacing: -0.5px;
            text-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}

        .header .subtitle {{
            font-size: 1.3em;
            opacity: 0.95;
            font-weight: 400;
            margin-bottom: 20px;
            letter-spacing: 0.5px;
        }}

        .header .date {{
            display: inline-block;
            background: rgba(255, 255, 255, 0.2);
            padding: 10px 25px;
            border-radius: 50px;
            font-size: 0.95em;
            font-weight: 500;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}

        .content {{
            padding: 60px 50px;
            background: white;
        }}

        .section {{
            margin-bottom: 50px;
            page-break-inside: avoid;
            animation: fadeIn 0.5s ease-out;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}

        .section:last-child {{
            margin-bottom: 0;
        }}

        h1 {{
            color: var(--primary);
            font-size: 2.2em;
            font-weight: 800;
            margin-bottom: 30px;
            margin-top: 50px;
            padding-bottom: 20px;
            border-bottom: 4px solid var(--primary);
            position: relative;
        }}

        h1::after {{
            content: '';
            position: absolute;
            bottom: -4px;
            left: 0;
            width: 80px;
            height: 4px;
            background: var(--accent);
        }}

        h1:first-child {{
            margin-top: 0;
        }}

        h2 {{
            color: var(--secondary);
            font-size: 1.7em;
            font-weight: 700;
            margin-top: 40px;
            margin-bottom: 25px;
            padding-left: 20px;
            border-left: 5px solid var(--secondary);
            position: relative;
            transition: all 0.3s ease;
        }}

        h2:hover {{
            padding-left: 25px;
            border-left-color: var(--accent);
        }}

        h3 {{
            color: var(--dark);
            font-size: 1.4em;
            font-weight: 600;
            margin-top: 30px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
        }}

        h3::before {{
            content: '▸';
            color: var(--primary);
            margin-right: 10px;
            font-size: 0.9em;
        }}

        h4 {{
            color: var(--gray);
            font-size: 1.15em;
            margin-top: 25px;
            margin-bottom: 15px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        p {{
            margin-bottom: 18px;
            text-align: justify;
            line-height: 1.8;
            color: #334155;
        }}

        ul, ol {{
            margin-left: 35px;
            margin-bottom: 20px;
        }}

        li {{
            margin-bottom: 12px;
            padding-left: 8px;
            line-height: 1.7;
        }}

        ul li {{
            list-style: none;
            position: relative;
        }}

        ul li::before {{
            content: '●';
            color: var(--primary);
            font-size: 0.8em;
            position: absolute;
            left: -20px;
            top: 2px;
        }}

        .highlight {{
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            padding: 25px;
            border-left: 5px solid var(--warning);
            margin: 25px 0;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            position: relative;
            overflow: hidden;
        }}

        .highlight::before {{
            content: '⚡';
            position: absolute;
            top: 15px;
            right: 20px;
            font-size: 2em;
            opacity: 0.2;
        }}

        .warning {{
            background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
            padding: 25px;
            border-left: 5px solid var(--danger);
            margin: 25px 0;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            position: relative;
            overflow: hidden;
        }}

        .warning::before {{
            content: '⚠️';
            position: absolute;
            top: 15px;
            right: 20px;
            font-size: 2em;
            opacity: 0.2;
        }}

        .success {{
            background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
            padding: 25px;
            border-left: 5px solid var(--success);
            margin: 25px 0;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            position: relative;
            overflow: hidden;
        }}

        .success::before {{
            content: '✓';
            position: absolute;
            top: 15px;
            right: 20px;
            font-size: 2.5em;
            opacity: 0.2;
        }}

        .info {{
            background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
            padding: 25px;
            border-left: 5px solid var(--info);
            margin: 25px 0;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            position: relative;
            overflow: hidden;
        }}

        .info::before {{
            content: 'ℹ';
            position: absolute;
            top: 15px;
            right: 20px;
            font-size: 2em;
            opacity: 0.2;
        }}

        table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin: 30px 0;
            background: white;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            border-radius: 12px;
            overflow: hidden;
        }}

        thead {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        }}

        th {{
            color: white;
            padding: 18px 20px;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 0.9em;
        }}

        td {{
            padding: 16px 20px;
            border-bottom: 1px solid var(--border);
            transition: all 0.2s ease;
        }}

        tr:last-child td {{
            border-bottom: none;
        }}

        tbody tr {{
            transition: all 0.2s ease;
        }}

        tbody tr:hover {{
            background: var(--light-gray);
            transform: scale(1.01);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}

        code {{
            background: #f1f5f9;
            padding: 4px 8px;
            border-radius: 6px;
            font-family: 'Monaco', 'Courier New', monospace;
            color: #e11d48;
            font-size: 0.9em;
            border: 1px solid #e2e8f0;
        }}

        pre {{
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            color: #f8fafc;
            padding: 25px;
            border-radius: 12px;
            overflow-x: auto;
            margin: 25px 0;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
            border: 1px solid #334155;
        }}

        pre code {{
            background: none;
            color: inherit;
            padding: 0;
            border: none;
        }}

        .divider {{
            height: 3px;
            background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 50%, var(--accent) 100%);
            margin: 60px 0;
            border-radius: 10px;
            opacity: 0.4;
        }}

        .footer {{
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            padding: 40px 50px;
            text-align: center;
            color: var(--gray);
            font-size: 0.95em;
            border-top: 3px solid var(--primary);
            position: relative;
        }}

        .footer p {{
            margin: 8px 0;
            line-height: 1.6;
        }}

        .footer strong {{
            color: var(--dark);
            font-weight: 600;
        }}

        .footer::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 50%, var(--accent) 100%);
        }}

        .badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            margin: 5px;
        }}

        .badge-primary {{
            background: var(--primary);
            color: white;
        }}

        .badge-success {{
            background: var(--success);
            color: white;
        }}

        .badge-warning {{
            background: var(--warning);
            color: white;
        }}

        blockquote {{
            margin: 25px 0;
            padding: 20px 30px;
            background: var(--light-gray);
            border-left: 5px solid var(--primary);
            border-radius: 0 12px 12px 0;
            font-style: italic;
            color: var(--gray);
        }}

        @media print {{
            body {{
                background: white;
                padding: 0;
            }}

            .container {{
                box-shadow: none;
                border-radius: 0;
            }}

            .header {{
                page-break-after: always;
            }}

            .section {{
                page-break-inside: avoid;
            }}

            .header::before {{
                display: none;
            }}

            tr {{
                page-break-inside: avoid;
            }}
        }}

        @media (max-width: 768px) {{
            body {{
                padding: 15px;
            }}

            .header {{
                padding: 50px 30px;
            }}

            .header h1 {{
                font-size: 2em;
            }}

            .header .subtitle {{
                font-size: 1.1em;
            }}

            .content {{
                padding: 30px 25px;
            }}

            h1 {{
                font-size: 1.8em;
            }}

            h2 {{
                font-size: 1.4em;
            }}

            h3 {{
                font-size: 1.2em;
            }}

            table {{
                font-size: 0.9em;
            }}

            th, td {{
                padding: 12px 10px;
            }}
        }}

        /* 스크롤바 스타일링 */
        ::-webkit-scrollbar {{
            width: 10px;
            height: 10px;
        }}

        ::-webkit-scrollbar-track {{
            background: var(--light-gray);
        }}

        ::-webkit-scrollbar-thumb {{
            background: var(--primary);
            border-radius: 5px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: var(--primary-dark);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-content">
                <h1>⚡ EV Investment Analysis Report</h1>
                <div class="subtitle">전기차 산업 투자 분석 보고서</div>
                <div class="date">📅 {date}</div>
            </div>
        </div>

        <div class="content">
            {content}
        </div>

        <div class="footer">
            <p><strong>생성 일시:</strong> {generated_time}</p>
            <p style="margin-top: 10px;">이 보고서는 참고용으로만 사용되어야 합니다. 투자 결정은 투자자 자신의 판단과 책임 하에 이루어져야 합니다.</p>
            <p style="margin-top: 20px; opacity: 0.6; font-size: 0.9em;">✨ Generated by EVI Agent System</p>
        </div>
    </div>
</body>
</html>"""

    def markdown_to_html(self, md_content: str, title: str = "Investment Report",
                         date: str = None) -> str:
        """
        Markdown을 HTML로 변환

        Args:
            md_content: Markdown 콘텐츠
            title: 보고서 제목
            date: 보고서 날짜

        Returns:
            HTML 문자열
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        generated_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Markdown을 HTML로 변환
        html_content = markdown.markdown(
            md_content,
            extensions=['extra', 'codehilite', 'toc', 'tables', 'fenced_code']
        )

        # 스타일 클래스 적용
        html_content = html_content.replace('<p>[WARNING]', '<div class="warning"><p><strong>[WARNING]</strong>')
        html_content = html_content.replace('<p>✅', '<div class="success"><p>✅')
        html_content = html_content.replace('<p>⚠️', '<div class="warning"><p>⚠️')
        html_content = html_content.replace('<p>[OK]', '<div class="success"><p><strong>[OK]</strong>')

        # 섹션 분리
        sections = html_content.split('<hr>')
        formatted_sections = []
        for section in sections:
            if section.strip():
                formatted_sections.append(f'<div class="section">{section}</div>')

        html_content = '<div class="divider"></div>'.join(formatted_sections)

        # 템플릿에 삽입
        html_output = self.html_template.format(
            title=title,
            date=date,
            content=html_content,
            generated_time=generated_time
        )

        return html_output

    def save_html(self, md_content: str, output_path: str,
                  title: str = "Investment Report", date: str = None):
        """
        Markdown을 HTML 파일로 저장

        Args:
            md_content: Markdown 콘텐츠
            output_path: 출력 파일 경로
            title: 보고서 제목
            date: 보고서 날짜
        """
        html_content = self.markdown_to_html(md_content, title, date)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"   [OK] HTML 저장 완료: {output_path}")

    def html_to_pdf(self, html_path: str, pdf_path: str):
        """
        HTML을 PDF로 변환
        
        브라우저 기반 변환 방법을 사용합니다 (가장 안정적)

        Args:
            html_path: HTML 파일 경로
            pdf_path: PDF 출력 경로
        """
        import subprocess
        import os
        
        print(f"\n   📄 HTML 파일이 생성되었습니다: {html_path}")
        print(f"   💡 PDF로 변환하려면 다음 방법 중 하나를 사용하세요:")
        print(f"\n   방법 1) 브라우저 사용 (권장):")
        print(f"      1. 아래 명령어로 HTML 파일을 브라우저에서 열기:")
        print(f"         open '{html_path}'")
        print(f"      2. 브라우저에서 Cmd+P (인쇄)")
        print(f"      3. 'PDF로 저장' 선택")
        
        # 자동으로 브라우저에서 열기
        try:
            if os.path.exists(html_path):
                subprocess.run(['open', html_path], check=False)
                print(f"\n   ✅ 브라우저에서 HTML 파일을 열었습니다!")
                print(f"   📌 Cmd+P를 누르고 'PDF로 저장'을 선택하세요.")
        except Exception as e:
            print(f"   [INFO] 자동 열기 실패: {e}")
        
        print(f"\n   방법 2) 명령줄 도구 사용:")
        print(f"      # Playwright 설치 (한 번만)")
        print(f"      pip install playwright && playwright install chromium")
        print(f"      # PDF 생성")
        print(f"      python3 -c \"from playwright.sync_api import sync_playwright; p = sync_playwright().start(); browser = p.chromium.launch(); page = browser.new_page(); page.goto('file://{os.path.abspath(html_path)}'); page.pdf(path='{pdf_path}'); browser.close()\"")
        print()

    def convert_markdown_file(self, md_path: str, generate_pdf: bool = True):
        """
        Markdown 파일을 HTML과 PDF로 변환

        Args:
            md_path: Markdown 파일 경로
            generate_pdf: PDF 생성 여부
        """
        md_path = Path(md_path)

        # Markdown 읽기
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # HTML 저장
        html_path = md_path.with_suffix('.html')
        self.save_html(md_content, str(html_path),
                      title="EV Investment Analysis Report",
                      date=datetime.now().strftime("%Y년 %m월"))

        # PDF 생성 (옵션)
        if generate_pdf:
            pdf_path = md_path.with_suffix('.pdf')
            self.html_to_pdf(str(html_path), str(pdf_path))
