# FruityIcon 도형 도구

PNG 스프라이트 경계를 측정하고 CSS를 생성합니다. 도형 예제 여섯 개가 포함되며
원본 그림과 글꼴은 제외됩니다. Pixel을 사용하려면 권리가 있는 글꼴 파일을
선택하세요. 파일은 로컬에서만 읽으며 업로드하지 않습니다. 새로고침 후 다시
선택해야 합니다. 로드 전에는 안내와 시스템 글꼴이 표시됩니다.

`deno task check`, `deno task test`, `deno task build`, `deno task demo`를
실행하고 `http://127.0.0.1:18210/demo/`를 여세요. Ctrl-C로 종료합니다. Deno
2.8+와 Python 3.10+가 필요합니다. `python3 scripts/generate-examples.py`로
예제를 다시 생성할 수 있습니다. 교체 이미지의 권리와 RGBA PNG 격자 형식은
사용자가 확인해야 합니다.

로컬 데모는 시작 시 읽은 필요한 공개 파일만 제공합니다.

코드와 기본 예제는 MIT, 문서 아이콘은 CC BY 4.0입니다.
[라이선스](LICENSE-SCOPE.json) · [의존성](DEPENDENCIES.md) ·
[예제 출처](examples/provenance.json).

제공된 라이트／다크 시트는 1536 × 1024, 8비트 RGBA PNG이며 512 px 셀을 3 × 2로
배치합니다. 파서는 비인터레이스 PNG를 지원하며 인코딩 16 MiB, 디코딩 64 MiB로
제한합니다. `deno task setup`은 설치된 도구를 확인하며 hook을 바꾸지 않습니다.
`deno task public:tool`은 목록을 내보내고 해시와 mode를 확인합니다.
`python3 scripts/measure-icons.py --check`는 생성 CSS와 보정값을 확인합니다.
