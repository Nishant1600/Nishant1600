// Line-art icons shared by the concept pages. Use: <svg><use href="#ic-audit"/></svg>
(function () {
  function sym(id, body) {
    return '<symbol id="ic-' + id + '" viewBox="0 0 100 100" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">' + body + '</symbol>';
  }
  var s = '<svg width="0" height="0" style="position:absolute"><defs>' +
    sym('audit', '<path d="M50 8 L84 20 V48 C84 70 68 86 50 92 C32 86 16 70 16 48 V20Z"/><circle cx="46" cy="46" r="14"/><path d="M56 56 L70 70"/><path d="M40 46 l5 5 l9 -10"/>') +
    sym('jarvis', '<rect x="40" y="14" width="20" height="40" rx="10"/><path d="M30 46 C30 64 70 64 70 46"/><path d="M50 64 V82 M36 84 H64"/><path d="M18 36 C12 46 12 56 18 66 M82 36 C88 46 88 56 82 66"/>') +
    sym('study', '<path d="M50 30 C38 22 22 22 10 28 V76 C22 70 38 70 50 78 C62 70 78 70 90 76 V28 C78 22 62 22 50 30Z"/><path d="M50 30 V78"/><path d="M20 42 C28 40 36 40 42 44 M20 54 C28 52 36 52 42 56 M58 44 C64 40 72 40 80 42 M58 56 C64 52 72 52 80 54"/><path d="M50 6 l3 7 l8 1 l-6 5 l2 8 l-7 -4 l-7 4 l2 -8 l-6 -5 l8 -1z"/>') +
    sym('mediscan', '<path d="M40 22 H60 V40 H78 V60 H60 V78 H40 V60 H22 V40 H40Z"/><path d="M10 28 V10 H28 M72 10 H90 V28 M90 72 V90 H72 M28 90 H10 V72"/>') +
    sym('orion', '<circle cx="28" cy="22" r="4"/><circle cx="72" cy="26" r="4"/><circle cx="40" cy="50" r="3"/><circle cx="50" cy="52" r="3"/><circle cx="60" cy="54" r="3"/><circle cx="30" cy="82" r="4"/><circle cx="74" cy="80" r="4"/><path d="M28 22 L72 26 M28 22 L40 50 M72 26 L60 54 M40 50 L60 54 M40 50 L30 82 M60 54 L74 80"/>') +
    sym('code', '<path d="M34 30 L14 50 L34 70 M66 30 L86 50 L66 70"/><circle cx="50" cy="46" r="12"/><path d="M59 55 L70 68"/>') +
    sym('c', '<path d="M74 28 C48 14 20 30 20 50 C20 70 48 86 74 72"/><path d="M12 12 l4 0 M84 88 l4 0"/>') +
    sym('rust', '<circle cx="50" cy="50" r="22"/><circle cx="50" cy="50" r="7"/><path d="M50 8 V28 M50 72 V92 M8 50 H28 M72 50 H92 M20 20 L34 34 M66 66 L80 80 M80 20 L66 34 M34 66 L20 80"/>') +
    sym('compass', '<circle cx="50" cy="50" r="38"/><path d="M50 16 L60 50 L50 84 L40 50Z"/><path d="M50 50 V50"/>') +
    sym('sign', '<path d="M50 10 V92"/><path d="M50 22 H78 L88 31 L78 40 H50"/><path d="M50 52 H22 L12 61 L22 70 H50"/>') +
    sym('python', '<path d="M50 10 C30 10 30 20 30 28 V36 H52 V40 H24 C14 40 12 50 12 56 C12 64 16 72 26 72 H32 V62 C32 54 38 50 46 50 H62 C68 50 72 46 72 40 V28 C72 18 64 10 50 10Z"/><circle cx="44" cy="22" r="2.5"/>') +
    sym('star', '<path d="M50 8 l11 24 l26 3 l-19 18 l5 26 l-23 -13 l-23 13 l5 -26 l-19 -18 l26 -3z"/>') +
    '</defs></svg>';
  document.body.insertAdjacentHTML('afterbegin', s);
})();
