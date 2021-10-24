let scrollAnimationTargets = document.querySelectorAll('.js-scrollAnimation');//画面をスクロールし、表示領域内に入ったときにアニメーションさせたい要素

window.addEventListener('scroll', function() {//スクロールしたとき

  var scroll = window.scrollY;//スクロール量を取得
  var screenHeight = window.innerHeight;//画面の高さを取得

  for(let target of scrollAnimationTargets) {
    var topPosition = target.getBoundingClientRect().top + scroll;//アニメーションさせたい要素のtop座標を取得
    var bottomPosition = target.getBoundingClientRect().bottom + scroll;//アニメーションさせたい要素のbottom座標を取得
    if (scroll < topPosition && bottomPosition < scroll + screenHeight) { // アニメーションさせたい要素が画面表示領域に入った場合の処理
      target.classList.add('is-animated');
    } else {
        if (target.classList.contains('is-animated')) {
            target.classList.remove('is-animated');
        }
    }
  }

});