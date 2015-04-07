syms a x y

% Attractor limits
x_min = (4*a^2-a^3)/16;
x_max = a/4;

% Functions
f(x)  = a*x*(1-x);
g(x)  = (x - x_min) / (x_max - x_min);
gi(y) = simplify(solve(g(x) == y, x));

% Functions:
%  f  : Attr  -> Attr
%  g  : Attr  -> [0,1]
%  gi : [0,1] -> Attr
% g o f o gi : [0,1] -> [0,1]

F(x) = simplify(g(f(gi(x))));

% Parameter
% From [Pisarchik]: 3.57 < a < 4
a_min = sym('357/100');
a_max = sym('4');
h(a)  = (a - a_min) / (a_max - a_min);
hi(y) = simplify(solve(h(a) == y, a));

% Discretization
syms A X MAX
FD = simplify(subs(MAX*F,{a,x},{hi(A/MAX),X/MAX}));

% Polynomial coefficients
C = simplify(coeffs(F,x));
CD = simplify(subs(MAX*C,{a,x},{hi(A/MAX),X/MAX}));


