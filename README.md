# aoaipy


### 한글 띄어쓰기
[PyKoSpacing](https://github.com/haven-jeon/PyKoSpacing)
pip install git+https://github.com/haven-jeon/PyKoSpacing.git


### 기타
```powershell
# pem 파일 퍼미션 문제
$pemfile="c:\ssh\vm1-ubuntu_key.pem"
icacls.exe $pemfile /reset
icacls.exe $pemfile /grant:r $Env:UserName":(R)"
icacls.exe $pemfile /inheritance:r

```