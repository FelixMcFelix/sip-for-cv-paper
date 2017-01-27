$latinlow = [char[]]([char]'a'..[char]'z')
$latinhigh = [char[]]([char]'A'..[char]'Z')

$chars = $latinlow + $latinhigh

foreach($c in $latinlow){
    magick -background white -fill black -font ../resources/DejaVuSans.ttf -pointsize 300 label:"$c" ../imgs/dejavu-sans/$c.png
}

foreach($c in $latinhigh){
    magick -background white -fill black -font ../resources/DejaVuSans.ttf -pointsize 300 label:"$c" ../imgs/dejavu-sans/$c-up.png
}