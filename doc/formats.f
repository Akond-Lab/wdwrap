
      DO 1000 IT=1,1000

   22 format(    8(i1,1x),                                      i2,1x,i2)
      read(5,22) MPAGE,NREF,MREF,IFSMV1,IFSMV2,ICOR1,ICOR2,IF3B,LD1,  LD2
      if(mpage.ne.9) goto 414
        stop
  414 continue
  649 format(     i1,    f15.6, d17.10, d13.6, f10.6,  d10.4, i2,    f11.0)
      read(5,649) jdphs, hjd0,  period, dpdt,  pshift, stdev, noise, seed
  217 format(     f14.6, f15.6, f13.6, 4f12.6)
      read(5,217) hjdst, hjdsp, hjdin, phstrt,phstop,phin,phn
    1 FORMAT(   4I2,                  2I4,   f13.6, d12.5,  f7.5, F8.2)
      READ(5,1) MODE,IPB,IFAT1,IFAT2, N1,N2, perr0, dperdt, the,  VUNIT
    2 FORMAT(   F6.5, d13.6, 2F10.4, F10.4, f9.3,  2f7.3,   f7.2)
      READ(5,2) E,    A,     F1,F2,  VGA,   XINCL, GR1,GR2, abunin
    6 FORMAT(   F7.4, 1X, f7.4, 2f7.3,     3d13.6,       4F7.3)
      read(5,6) tavh,     tavc, alb1,alb2, poth,potc,rm, xbol1,xbol2,ybol1,ybol2
c  Third body
  101 format(     d12.6, d14.7, f11.5,  f9.6, f10.7,  f17.8)
      read(5,101) a3b,   p3b,   xinc3b, e3b,  perr3b, tconj3b
    4 FORMAT(   i3,    2d13.5,    4F7.3,       F8.4, d10.4, F8.3, F8.4,   f9.6)
      READ(5,4) iband, HLUM,CLUM, XH,xc,yh,yc, EL3,  opsf,  ZERO, FACTOR, wl

      if(mpage.ne.3) goto 897
c       Spectral
 2048   format(      d11.5,  f9.4, f9.2, i3)
        read(5,2048) binwm1, sc1,  sl1,  nf1
        do 86 iln=1,lpimax
  138     format(     f9.6,      d12.5,      f10.5,       i5)
          read(5,138) wll1(iln), ewid1(iln), depth1(iln), kks(1,iln)
          if(wll1(iln).lt.0.d0) goto 89
          86 continue
        89 continue

        read(5,2048) binwm2,sc2,sl2,nf2
        do 99 iln=1,lpimax
          read(5,138) wll2(iln),ewid2(iln),depth2(iln),kks(2,iln)
          if(wll2(iln).lt.0.d0) goto 91
   99     continue
   91   continue
  897 continue

c     Spots
      DO 88 KP=1,2
        DO 87 I=1,ispmax
   85     FORMAT(    4f9.5)
          READ(5,85) XLAT(KP,I),XLONG(KP,I),RADSP(KP,I),TEMSP(KP,I)
          IF(XLAT(KP,I).GE.200.d0) GOTO 88
   87   CONTINUE
   88 CONTINUE

c     Clouds
      do 62 i=1,iclmax
   63   format(    3f9.4,                 f7.4,   d11.4,  f9.4,   d11.3,    f9.4,    f7.3)
        read(5,63) xcl(i),ycl(i),zcl(i),  rcl(i), op1(i), fcl(i), edens(i), xmue(i), encl(i)
        if(xcl(i).gt.100.d0) goto 66
   62 continue
   66 continue









 1000 CONTINUE


