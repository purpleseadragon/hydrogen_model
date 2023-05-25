# File for functions related to PEM model

# PEM model
# takes as input a vector of electricity input rates
# returns a vector of hydrogen output rates
"Calculates hydrogen outputs from PEM electrolysis given electricity inputs"
function pem(input::Vector{Float64}, efficiency::Float64=0.6)
    output = zeros(Float64, length(input))
    for i in 1:length(input)
        output[i] = input[i] * efficiency
    end
    return output
end