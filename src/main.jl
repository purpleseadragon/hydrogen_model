print("hello world\n")

# Alkaline model
# takes as input a vector of electricity input rates
# returns a vector of hydrogen output rates
function alkaline(input::Vector{Float64}, efficiency::Float64=0.5)
    output = zeros(Float64, length(input))
    for i in 1:length(input)
        output[i] = input[i] * efficiency
    end
    return output
end

# PEM model
# takes as input a vector of electricity input rates
# returns a vector of hydrogen output rates
function pem(input::Vector{Float64}, efficiency::Float64=0.6)
    output = zeros(Float64, length(input))
    for i in 1:length(input)
        output[i] = input[i] * efficiency
    end
    return output
end

input = [1.0, 2.0, 3.0]
print(typeof(input))

print(alkaline(input))