function Y = clogistic(a,x,N,T)

if nargin < 4, T = 0; end

for i = 1:T
%    x = -(16*(a/4 - x).*(a.^3 - 4*a.^2 + 8*a - 16*x))./(a.*(a - 2).^4);
%    x = a .* x .* (1-x);
    x = -(a.*(a - 2).*(x - 1).*(2*a - 2*a.*x + a.^2.*x - a.^2 + 8))/16;
end

Y = zeros(N+1,length(a(:)));
Y(1,:) = x;
for i = 1:N
    x = -(a.*(a - 2).*(x - 1).*(2*a - 2*a.*x + a.^2.*x - a.^2 + 8))/16;
%    x = a .* x .* (1-x);
    Y(i+1,:) = x;
end

end