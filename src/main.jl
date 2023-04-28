print("hello world\n")

# Alkaline model


# PEM model

function fibonacci(n::Int64)
    if n == 0
        return 0
    elseif n == 1
        return 1
    else
        fib = zeros(Int64, n+1)
        fib[1] = 0
        fib[2] = 1
        for i in 3:(n+1)
            fib[i] = fib[i-1] + fib[i-2]
        end
        return fib[n+1]
    end
end

fibonacci(100)