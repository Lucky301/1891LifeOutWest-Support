# 1891: Life Out West — Support

SupraCore의 **1891: 서부에서 살아가기 / 1891: Life Out West** 공개 지원·개인정보처리방침 사이트입니다.

문의: [support@supracore.co.kr](mailto:support@supracore.co.kr)

| App Store Connect 항목 | 한국어 | English |
| --- | --- | --- |
| Support URL | [지원](https://lucky301.github.io/1891LifeOutWest-Support/ko/support/) | [Support](https://lucky301.github.io/1891LifeOutWest-Support/en/support/) |
| Privacy Policy URL | [개인정보처리방침](https://lucky301.github.io/1891LifeOutWest-Support/ko/privacy/) | [Privacy Policy](https://lucky301.github.io/1891LifeOutWest-Support/en/privacy/) |
| 문의·Contact | [이메일 문의 안내](https://lucky301.github.io/1891LifeOutWest-Support/ko/support/#contact) | [Contact](https://lucky301.github.io/1891LifeOutWest-Support/en/support/#contact) |
| 개인정보 권리·삭제 요청 안내 | [권리 요청](https://lucky301.github.io/1891LifeOutWest-Support/ko/privacy/#rights) | [Privacy requests](https://lucky301.github.io/1891LifeOutWest-Support/en/privacy/#rights) |

Marketing URL: <https://lucky301.github.io/1891LifeOutWest-Support/>

링크 목록은 [app-store-links.json](app-store-links.json)에 있으며, 게시된 사이트에서도 [JSON으로 확인](https://lucky301.github.io/1891LifeOutWest-Support/app-store-links.json)할 수 있습니다.

Apple 표준 EULA: <https://www.apple.com/legal/internet-services/itunes/dev/stdeula/>

## 버그 제보

일반 버그는 [Issues](https://github.com/Lucky301/1891LifeOutWest-Support/issues)에 남길 수 있습니다. **공개 게시물**이므로 이메일 주소, 구매 영수증, 저장 파일, 암호와 같은 개인정보를 올리지 마세요. 개인정보·구매·저장 자료가 필요한 문의는 지원 이메일을 이용하세요. GitHub 계정 없이 이메일로 문의할 수 있습니다.

## 수정과 게시

GitHub Pages는 **main 브랜치의 `/docs` 폴더**를 게시합니다. 빌드에는 Python 3 표준 라이브러리만 사용합니다.

1. `site/content.py`에서 한국어·영어 문안을, `site/publication-config.json`에서 운영자·문의·시행일·보관 기준을 수정합니다.
2. `python3 site/build.py`와 `python3 site/validate.py --release`를 실행합니다.
3. `site`의 변경 사항과 생성된 `docs`를 함께 커밋하여 `main`에 푸시합니다.
4. GitHub Pages 배포 후 두 언어의 공개 URL을 확인합니다.

문의는 이메일 대응에 필요한 기간 보관 후 목적 달성 시 삭제하는 기준으로 작성했습니다. 법령상 별도 보관 의무가 있는 기록과 GitHub·Apple·Unity 등 외부 서비스의 기록은 각 적용 기준을 따릅니다. 운영자는 실제 지원 처리와 배포 SDK가 바뀌면 정책도 함께 갱신해야 합니다.

이 저장소에는 앱의 게임 소스, 사용자 저장 파일, 서명 인증서나 인증 토큰을 포함하지 않습니다. 개인정보 안내는 현재 앱 소스·SDK 문서·호스팅을 기준으로 작성했으며, 최종 배포 빌드의 App Privacy 응답은 별도로 확인해야 합니다.

## English

Public support and privacy pages for **1891: Life Out West** by SupraCore.

Contact **support@supracore.co.kr**. Public GitHub Issues are suitable for general bug reports; send personal or purchase-related material privately by email.

GitHub Pages publishes `/docs` from `main`. Edit `site/content.py` and `site/publication-config.json`, run `python3 site/build.py` and `python3 site/validate.py --release`, then commit the source and generated pages together.

The pages reflect the current app source, SDK documentation and GitHub Pages hosting. Keep them aligned with actual support practices and the final shipping build.
