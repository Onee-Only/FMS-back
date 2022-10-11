# FMS Backend 사용 설명서

<br>

## 요구 사항

-   python 3.9 필요
-   따라올 의지 필요

<br>

## 개발환경 세팅

<br>

### pipenv 설치

> 가상환경을 설치한다.

`pip install pipenv`

<br>

### 가상환경 생성 및 

1. 프로젝트를 가져올 디렉토리로 이동한다. (cd 사용)
2. 프로젝트를 가져온다.
   
        git clone https://github.com/SiuuuSiuuu/FMS-back.git
    
3. 가상환경을 생성한다.

        pipenv --three

4. 패키지를 다운한다.
   
        pipenv install --dev

### 앱 실행

<br>

> 무조건 루트 디렉토리에서 한다.


        python manage.py runserver


성공 시 :

        Django version 3.2, using settings 'config.settings'
        Starting development server at http://127.0.0.1:8000/
        Quit the server with CONTROL-C.
    

아니면 김원욱에게 문의

> 실행 중지하려면 Ctrl + C
