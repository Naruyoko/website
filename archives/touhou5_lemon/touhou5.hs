import Control.Monad
import Data.List
import System.Environment
import System.IO
import System.Win32.Console
main=setConsoleOutputCP 65001>>hSetEncoding stdout utf8>>getArgs>>=(\d->putStr$unlines((\a->join[('🎁':show i):join(map(\(a,b)->('📅':show b):map(show.map fromRational)a++[""])g)++[""]|d,((g,_),i)<-zip a[1..]]++['🍋':(show.snd.last)a]).take 10.tail$iterate(\(_,n)->(\g->(g,n+snd(last g)))$(\(a,b:_)->a++[b]).break(null.fst)$iterate(\(t:b,y)->([(\(e,c:r)->((sum.foldl1(zipWith(\x y->x*y*1000`max`x+y))$t:b)<$e)++(\x->if x<1/1000 then 0 else x)(c*99/100):r).break(>0)$t|sum t>0,t<-genericTake(y*10+10)$repeat t]++b,y+1))(replicate 5$map(toRational.(`mod`2)).takeWhile(>0).iterate(`div`2)$n+10,0))([],0))).not.null