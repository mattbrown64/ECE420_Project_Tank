import qrcode
code = qrcode.make('Friend!')
code.save("qrcode_friend.png")


code = qrcode.make('Enemy!')
code.save("qrcode_enemy.png")


code = qrcode.make('BiggerEnemy!')
code.save("qrcode_bigger_enemy.png")


code = qrcode.make('Lover!')
code.save("qrcode_lover.png")