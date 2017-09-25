load('vars');
maxxRectum=0;
for i = 1:25
    if nnz(rectumIntersecting(:,:,rectumSlices(i)))>maxxRectum
        maxiRectum=i;
    end
    maxxRectum=max(nnz(rectumIntersecting(:,:,rectumSlices(i))),maxxRectum);
    
end
maxxBladder=0;
for i = 1:10
    if nnz(bladderIntersecting(:,:,bladderSlices(i)))>maxxBladder
        maxiBladder=i;
    end
    maxxBladder=max(nnz(bladderIntersecting(:,:,bladderSlices(i))),maxxBladder);
    
end


    