# File for functions and variables related to alkaline model




"calculates hydrogen output rates from alkaline electrolysis given electricity inputs"
function alkaline(input::Vector{Float64}, efficiency::Float64=1, period::Float64=1.0)
    # working in kWh, kg and hours
    base = 55 # kWh/kg
    output = zeros(Float64, length(input))
    for i in 1:length(input)
        output[i] = input[i] * efficiency * base
    end
    return output
end